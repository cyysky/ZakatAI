"""
Vector Store Service - ChromaDB vector storage for RAG
"""
import os
from typing import List, Dict, Any, Optional
from app.core.config import settings

# Try to import chromadb, fallback to simple implementation if not available
try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False


class VectorStoreService:
    """Service for storing and retrieving document embeddings."""

    def __init__(self):
        self.db_dir = settings.CHROMA_DB_DIR
        self.collection_name = "zakat_knowledge"
        self.client = None
        self.collection = None

        if CHROMADB_AVAILABLE:
            self._init_chroma()

    def _init_chroma(self):
        """Initialize ChromaDB client."""
        try:
            os.makedirs(self.db_dir, exist_ok=True)
            self.client = chromadb.Client(Settings(
                persist_directory=self.db_dir,
                anonymized_telemetry=False
            ))
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": "Zakat Knowledge Base"}
            )
        except Exception as e:
            print(f"Warning: Could not initialize ChromaDB: {e}")
            self.client = None
            self.collection = None

    async def add_documents(
        self,
        documents: List[Dict[str, str]],
        embeddings: Optional[List[List[float]]] = None
    ):
        """Add documents to the vector store."""
        if not self.collection:
            return {"success": False, "error": "Vector store not initialized"}

        ids = [f"doc_{i}" for i in range(len(documents))]
        texts = [doc.get("text", "") for doc in documents]
        metadatas = [doc.get("metadata", {}) for doc in documents]

        # If embeddings not provided, use simple hash-based vectors
        if embeddings is None:
            embeddings = self._simple_embeddings(texts)

        try:
            self.collection.add(
                ids=ids,
                documents=texts,
                embeddings=embeddings,
                metadatas=metadatas
            )
            return {"success": True, "count": len(documents)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def similarity_search(
        self,
        query: str,
        n_results: int = 3
    ) -> List[Dict[str, Any]]:
        """Search for similar documents."""
        if not self.collection:
            return self._get_fallback_results(query)

        query_embedding = self._simple_embeddings([query])[0]

        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )

            documents = []
            if results.get("documents"):
                for i, doc in enumerate(results["documents"][0]):
                    documents.append({
                        "text": doc,
                        "metadata": results["metadatas"][0][i] if results.get("metadatas") else {},
                        "distance": results["distances"][0][i] if results.get("distances") else 0
                    })

            return documents

        except Exception as e:
            print(f"Search error: {e}")
            return self._get_fallback_results(query)

    def _simple_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate simple embeddings using hash-based approach."""
        import hashlib
        import numpy as np

        embeddings = []
        for text in texts:
            # Create a simple deterministic embedding
            hash_val = hashlib.sha256(text.encode()).digest()
            # Convert to normalized vector
            vector = np.frombuffer(hash_val, dtype=np.float32)
            vector = vector / np.linalg.norm(vector)
            embeddings.append(vector.tolist())

        return embeddings

    def _get_fallback_results(self, query: str) -> List[Dict[str, Any]]:
        """Return fallback results when vector store is not available."""
        # Common FAQ knowledge base
        knowledge_base = [
            {
                "text": "Untuk memohon bantuan Zakat, anda perlu melengkapkan borang permohonan dan menyediakan dokumen sokongan seperti salinan IC, slip gaji terkini, dan bil utiliti. Permohonan boleh dibuat di pejabat Zakat atau secara online.",
                "metadata": {"topic": "permohonan", "category": "faq"}
            },
            {
                "text": "Syarat kelayakan menerima bantuan Zakat adalah: (1) Warganegara Malaysia atau bermastautin di Malaysia, (2) Muslim, (3) Pendapatan isi rumah di bawah paras garis panduan (RM1169 sebulan untuk fakir), (4) Mempunyai dokumen sokongan yang sah.",
                "metadata": {"topic": "kelayakan", "category": "faq"}
            },
            {
                "text": "Sistem Zakat menyediakan pelbagai jenis bantuan termasuk: bantuan bulanan untuk fakir dan miskin, bantuan pendidikan (yayasan buku, tuisyen), bantuan perubatan, bantuan bencana, dan bantuan perniagaan untuk asnaf yang tertentu.",
                "metadata": {"topic": "jenis_bantuan", "category": "faq"}
            },
            {
                "text": "Masa pemprosesan permohonan Zakat biasanya mengambil masa 14-30 hari bekerja. Tempoh ini bergantung kepada kesempurnaan dokumen yang disediakan dan semakan yang diperlukan.",
                "metadata": {"topic": "tempoh", "category": "faq"}
            },
            {
                "text": "Untuk semak status permohonan, anda boleh menggunakan nombor rujukan yang diberikan semasa menghantar permohonan. Hubungi pejabat Zakat atau gunakan sistem pertanyaan dalam talian.",
                "metadata": {"topic": "status", "category": "faq"}
            }
        ]

        # Simple keyword matching
        query_lower = query.lower()
        results = []

        for kb in knowledge_base:
            text_lower = kb["text"].lower()
            # Calculate simple relevance score
            score = 0
            keywords = query_lower.split()

            for keyword in keywords:
                if keyword in text_lower:
                    score += 1

            if score > 0:
                results.append({
                    "text": kb["text"],
                    "metadata": kb["metadata"],
                    "distance": 1.0 / (score + 1)  # Lower distance = higher relevance
                })

        # Sort by relevance and return top results
        results.sort(key=lambda x: x["distance"])
        return results[:3]

    async def initialize_knowledge_base(self):
        """Initialize the knowledge base with default documents."""
        default_documents = [
            {
                "text": "Sistem Zakat adalah badan yang bertanggungjawab untuk mentadbir hal ehwal agama Islam dan mengagihkan Zakat kepada yang berhak.",
                "metadata": {"topic": "zakat", "category": "info"}
            },
            {
                "text": "Zakat adalah salah satu daripada pillar Islam. Zakat wajib dibayar oleh setiap Muslim yang memenuhi syarat iaitu: cukup nisab (bersaldo sekurang-kurangnya RM1169 untuk emas) dan cukup haul (milik selama setahun).",
                "metadata": {"topic": "zakat", "category": "info"}
            },
            {
                "text": "Asnaf (penerima Zakat) yang wajib menerima bantuan Zakat adalah lapan kategori: (1) Fakir - tiada langsung pekerjaan/pendapatan, (2) Miskin - ada pekerjaan tetapi tidak mencukupi, (3) Amil - pengutip Zakat, (4) Muallaf - Muslim baru, (5) Riqab - hamba abdi, (6) Gharim - orang yang berhutang, (7) Fisabilillah - berjuang di jalan Allah, (8) Ibn Sabil - musafir yang kehabisan bekalan.",
                "metadata": {"topic": "asnaf", "category": "info"}
            },
            {
                "text": "Permohonan Zakat boleh dibuat secara online melalui sistem atau secara fizikal di pejabat Zakat. Pemohon perlu menyediakan: IC diri dan keluarga, slip gaji 3 bulan terkini, salinan bank statement, dan bills utiliti.",
                "metadata": {"topic": "permohonan", "category": "panduan"}
            },
            {
                "text": "Bantuan Zakat bulanan untuk fakir adalah sehingga RM500 sebulan bergantung kepada bilangan ahli keluarga dan keperluan. Bantuan pendidikan sehingga RM3000 setahun untuk setiap anak yang bersekolah.",
                "metadata": {"topic": "bantuan", "category": "panduan"}
            }
        ]

        await self.add_documents(default_documents)
        return {"success": True, "message": "Knowledge base initialized"}