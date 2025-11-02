/*
 * Trust M RSA Key Generation Example
 * Generates RSA key pair (2048-bit) and saves to files
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <openssl/rsa.h>
#include <openssl/pem.h>
#include <openssl/err.h>
#include <openssl/bn.h>

#define KEY_SIZE 2048
#define EXPONENT RSA_F4  // 65537

void print_usage(const char *prog) {
    printf("Usage: %s <private_key_file> <public_key_file>\n", prog);
    printf("\nExample:\n");
    printf("  %s private.pem public.pem\n", prog);
    printf("\nDescription:\n");
    printf("  Generates a 2048-bit RSA key pair\n");
    printf("  Saves private key to <private_key_file>\n");
    printf("  Saves public key to <public_key_file>\n");
}

int main(int argc, char *argv[]) {
    RSA *rsa = NULL;
    BIGNUM *bn = NULL;
    FILE *priv_file = NULL;
    FILE *pub_file = NULL;
    int ret = 1;

    if (argc != 3) {
        print_usage(argv[0]);
        return 1;
    }

    const char *priv_key_file = argv[1];
    const char *pub_key_file = argv[2];

    printf("[INFO] RSA Key Generation Tool\n");
    printf("[INFO] Key size: %d bits\n", KEY_SIZE);
    printf("[INFO] Public exponent: %ld\n", (long)EXPONENT);

    // Initialize OpenSSL
    OpenSSL_add_all_algorithms();
    ERR_load_crypto_strings();

    // Create BIGNUM for exponent
    bn = BN_new();
    if (!bn) {
        fprintf(stderr, "[ERROR] Failed to create BIGNUM\n");
        goto cleanup;
    }

    if (!BN_set_word(bn, EXPONENT)) {
        fprintf(stderr, "[ERROR] Failed to set exponent\n");
        goto cleanup;
    }

    // Generate RSA key pair
    printf("[INFO] Generating RSA key pair...\n");
    rsa = RSA_new();
    if (!rsa) {
        fprintf(stderr, "[ERROR] Failed to create RSA structure\n");
        goto cleanup;
    }

    if (!RSA_generate_key_ex(rsa, KEY_SIZE, bn, NULL)) {
        fprintf(stderr, "[ERROR] Failed to generate RSA key pair\n");
        ERR_print_errors_fp(stderr);
        goto cleanup;
    }

    printf("[OK] RSA key pair generated successfully\n");

    // Save private key
    printf("[INFO] Saving private key to %s...\n", priv_key_file);
    priv_file = fopen(priv_key_file, "wb");
    if (!priv_file) {
        perror("[ERROR] Failed to open private key file");
        goto cleanup;
    }

    if (!PEM_write_RSAPrivateKey(priv_file, rsa, NULL, NULL, 0, NULL, NULL)) {
        fprintf(stderr, "[ERROR] Failed to write private key\n");
        ERR_print_errors_fp(stderr);
        goto cleanup;
    }

    printf("[OK] Private key saved to %s\n", priv_key_file);

    // Save public key
    printf("[INFO] Saving public key to %s...\n", pub_key_file);
    pub_file = fopen(pub_key_file, "wb");
    if (!pub_file) {
        perror("[ERROR] Failed to open public key file");
        goto cleanup;
    }

    if (!PEM_write_RSAPublicKey(pub_file, rsa)) {
        fprintf(stderr, "[ERROR] Failed to write public key\n");
        ERR_print_errors_fp(stderr);
        goto cleanup;
    }

    printf("[OK] Public key saved to %s\n", pub_key_file);
    printf("\n[SUCCESS] RSA key pair generation completed\n");
    
    ret = 0;

cleanup:
    if (priv_file) fclose(priv_file);
    if (pub_file) fclose(pub_file);
    if (rsa) RSA_free(rsa);
    if (bn) BN_free(bn);
    ERR_free_strings();
    EVP_cleanup();

    return ret;
}
