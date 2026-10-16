FROM eclipse-temurin:21-jdk-jammy

# Install maven
RUN apt-get update && apt-get install -y maven && rm -rf /var/lib/apt/lists/*

# Create sandbox non-root user
RUN useradd -m -u 1001 sandboxuser

WORKDIR /home/sandboxuser/app

# Copy template pom and pre-warm dependencies
COPY pom.xml .
RUN chown -R sandboxuser:sandboxuser /home/sandboxuser

USER sandboxuser

# Download all dependencies into local maven cache (~/.m2)
RUN mvn dependency:go-offline

# Ready to compile and run snippets offline with mvn -o
CMD ["mvn", "-o", "test-compile"]
