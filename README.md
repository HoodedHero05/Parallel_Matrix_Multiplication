# Parallel_Matrix_Multiplication

Overview

This project implements a parallelized divide-and-conquer matrix multiplication system using a microservice-based architecture. Large matrices are divided into smaller submatrices, multiplied in parallel across multiple Docker containers, and then aggregated to produce the final matrix.

The system consists of four microservices:

Uploader Service: Accepts matrix input from the user or generates matrices of a specified size.

Divider Service: Splits matrices into smaller submatrices.

Multiplication Services: Compute the product of assigned submatrix pairs in parallel.

Aggregator Service: Combines partial results into the final matrix.

All services communicate via REST APIs over a shared Docker network and run in Docker containers to ensure consistent, isolated environments.

#Setup
1. Clone the repository

  git clone <repository_url>
  cd <repository_folder>


2. Run the setup script (cross-platform)

  python setup.py

3. Start the system

  docker-compose up --build
