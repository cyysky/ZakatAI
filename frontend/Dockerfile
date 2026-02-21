FROM node:20-alpine

WORKDIR /app

# Copy package files
COPY package.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Expose port
EXPOSE 7890

# Run the application
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "7890"]