#include <stddef.h>
#include <stdint.h>
#include <emscripten/emscripten.h>
#include "src/api.h"
#include "src/sign.h"

EMSCRIPTEN_KEEPALIVE
int dilithium3_keypair(uint8_t *pk, uint8_t *sk)
{
  return pqcrystals_dilithium3_ref_keypair(pk, sk);
}

EMSCRIPTEN_KEEPALIVE
int dilithium3_keypair_from_seed(uint8_t *pk, uint8_t *sk, const uint8_t *seed)
{
  return dilithium3_keypair_from_seed_impl(pk, sk, seed);
}

EMSCRIPTEN_KEEPALIVE
int dilithium3_sign(uint8_t *sig, size_t *siglen,
                    const uint8_t *msg, size_t msglen,
                    const uint8_t *sk)
{
  return pqcrystals_dilithium3_ref_signature(sig, siglen, msg, msglen, NULL, 0, sk);
}

EMSCRIPTEN_KEEPALIVE
int dilithium3_verify(const uint8_t *sig, size_t siglen,
                      const uint8_t *msg, size_t msglen,
                      const uint8_t *pk)
{
  return pqcrystals_dilithium3_ref_verify(sig, siglen, msg, msglen, NULL, 0, pk);
}
