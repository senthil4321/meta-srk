/*
 * Trust M RSA Sign Example
 * Signs data using RSA private key with SHA-256
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <openssl/rsa.h>
#include <openssl/pem.h>
#include <openssl/err.h>
#include <openssl/sha.h>

#define BUFFER_SIZE 4096

void print_usage(const char *prog) {
    printf("Usage: %s <private_key_file> <data_file> <signature_file>\n", prog);
    printf("\nExample:\n");
    printf("  %s private.pem message.txt signature.bin\n", prog);
    printf("\nDescription:\n");
    printf("  Signs data from <data_file> using RSA private key\n");
    printf("  Uses SHA-256 for hashing\n");
    printf("  Saves signature to <signature_file>\n");
}

int main(int argc, char *argv[]) {
    RSA *rsa = NULL;
    FILE *key_file = NULL;
    FILE *data_file = NULL;
    FILE *sig_file = NULL;
    unsigned char *data = NULL;
    unsigned char hash[SHA256_DIGEST_LENGTH];
    unsigned char *signature = NULL;
    unsigned int sig_len;
    long data_len;
    int ret = 1;

    if (argc != 4) {
        print_usage(argv[0]);
        return 1;
    }

    const char *priv_key_file = argv[1];
    const char *data_file_path = argv[2];
    const char *sig_file_path = argv[3];

    printf("[INFO] RSA Signature Tool\n");
    printf("[INFO] Hash algorithm: SHA-256\n");

    // Initialize OpenSSL
    OpenSSL_add_all_algorithms();
    ERR_load_crypto_strings();

    // Load private key
    printf("[INFO] Loading private key from %s...\n", priv_key_file);
    key_file = fopen(priv_key_file, "rb");
    if (!key_file) {
        perror("[ERROR] Failed to open private key file");
        goto cleanup;
    }

    rsa = PEM_read_RSAPrivateKey(key_file, NULL, NULL, NULL);
    if (!rsa) {
        fprintf(stderr, "[ERROR] Failed to read private key\n");
        ERR_print_errors_fp(stderr);
        goto cleanup;
    }

    printf("[OK] Private key loaded (key size: %d bits)\n", RSA_size(rsa) * 8);

    // Read data to sign
    printf("[INFO] Reading data from %s...\n", data_file_path);
    data_file = fopen(data_file_path, "rb");
    if (!data_file) {
        perror("[ERROR] Failed to open data file");
        goto cleanup;
    }

    fseek(data_file, 0, SEEK_END);
    data_len = ftell(data_file);
    fseek(data_file, 0, SEEK_SET);

    if (data_len <= 0 || data_len > 1024 * 1024) {
        fprintf(stderr, "[ERROR] Invalid data file size: %ld bytes\n", data_len);
        goto cleanup;
    }

    data = malloc(data_len);
    if (!data) {
        fprintf(stderr, "[ERROR] Failed to allocate memory for data\n");
        goto cleanup;
    }

    if (fread(data, 1, data_len, data_file) != (size_t)data_len) {
        fprintf(stderr, "[ERROR] Failed to read data file\n");
        goto cleanup;
    }

    printf("[OK] Read %ld bytes of data\n", data_len);

    // Calculate SHA-256 hash
    printf("[INFO] Calculating SHA-256 hash...\n");
    SHA256(data, data_len, hash);
    
    printf("[INFO] Hash (first 16 bytes): ");
    for (int i = 0; i < 16; i++) {
        printf("%02x", hash[i]);
    }
    printf("...\n");

    // Sign the hash
    printf("[INFO] Signing hash with RSA private key...\n");
    signature = malloc(RSA_size(rsa));
    if (!signature) {
        fprintf(stderr, "[ERROR] Failed to allocate memory for signature\n");
        goto cleanup;
    }

    if (!RSA_sign(NID_sha256, hash, SHA256_DIGEST_LENGTH, signature, &sig_len, rsa)) {
        fprintf(stderr, "[ERROR] Failed to sign data\n");
        ERR_print_errors_fp(stderr);
        goto cleanup;
    }

    printf("[OK] Signature created (%u bytes)\n", sig_len);

    // Save signature
    printf("[INFO] Saving signature to %s...\n", sig_file_path);
    sig_file = fopen(sig_file_path, "wb");
    if (!sig_file) {
        perror("[ERROR] Failed to open signature file");
        goto cleanup;
    }

    if (fwrite(signature, 1, sig_len, sig_file) != sig_len) {
        fprintf(stderr, "[ERROR] Failed to write signature\n");
        goto cleanup;
    }

    printf("[OK] Signature saved to %s\n", sig_file_path);
    printf("\n[SUCCESS] Data signed successfully\n");
    
    ret = 0;

cleanup:
    if (key_file) fclose(key_file);
    if (data_file) fclose(data_file);
    if (sig_file) fclose(sig_file);
    if (rsa) RSA_free(rsa);
    if (data) free(data);
    if (signature) free(signature);
    ERR_free_strings();
    EVP_cleanup();

    return ret;
}
