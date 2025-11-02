/*
 * Trust M RSA Verify Example
 * Verifies RSA signature using public key
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <openssl/rsa.h>
#include <openssl/pem.h>
#include <openssl/err.h>
#include <openssl/sha.h>

void print_usage(const char *prog) {
    printf("Usage: %s <public_key_file> <data_file> <signature_file>\n", prog);
    printf("\nExample:\n");
    printf("  %s public.pem message.txt signature.bin\n", prog);
    printf("\nDescription:\n");
    printf("  Verifies RSA signature using public key\n");
    printf("  Uses SHA-256 for hashing\n");
    printf("  Returns 0 if signature is valid, 1 otherwise\n");
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

    const char *pub_key_file = argv[1];
    const char *data_file_path = argv[2];
    const char *sig_file_path = argv[3];

    printf("[INFO] RSA Signature Verification Tool\n");
    printf("[INFO] Hash algorithm: SHA-256\n");

    // Initialize OpenSSL
    OpenSSL_add_all_algorithms();
    ERR_load_crypto_strings();

    // Load public key
    printf("[INFO] Loading public key from %s...\n", pub_key_file);
    key_file = fopen(pub_key_file, "rb");
    if (!key_file) {
        perror("[ERROR] Failed to open public key file");
        goto cleanup;
    }

    rsa = PEM_read_RSAPublicKey(key_file, NULL, NULL, NULL);
    if (!rsa) {
        fprintf(stderr, "[ERROR] Failed to read public key\n");
        ERR_print_errors_fp(stderr);
        goto cleanup;
    }

    printf("[OK] Public key loaded (key size: %d bits)\n", RSA_size(rsa) * 8);

    // Read data
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

    // Read signature
    printf("[INFO] Reading signature from %s...\n", sig_file_path);
    sig_file = fopen(sig_file_path, "rb");
    if (!sig_file) {
        perror("[ERROR] Failed to open signature file");
        goto cleanup;
    }

    fseek(sig_file, 0, SEEK_END);
    sig_len = ftell(sig_file);
    fseek(sig_file, 0, SEEK_SET);

    signature = malloc(sig_len);
    if (!signature) {
        fprintf(stderr, "[ERROR] Failed to allocate memory for signature\n");
        goto cleanup;
    }

    if (fread(signature, 1, sig_len, sig_file) != sig_len) {
        fprintf(stderr, "[ERROR] Failed to read signature file\n");
        goto cleanup;
    }

    printf("[OK] Read %u bytes of signature\n", sig_len);

    // Verify signature
    printf("[INFO] Verifying signature...\n");
    int verify_result = RSA_verify(NID_sha256, hash, SHA256_DIGEST_LENGTH, signature, sig_len, rsa);
    
    if (verify_result == 1) {
        printf("\n[SUCCESS] ✓ Signature is VALID\n");
        ret = 0;
    } else {
        printf("\n[FAILED] ✗ Signature is INVALID\n");
        ERR_print_errors_fp(stderr);
        ret = 1;
    }

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
