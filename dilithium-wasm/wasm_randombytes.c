#include <stddef.h>
#include <stdint.h>
#include <emscripten/emscripten.h>
#include "src/randombytes.h"

void randombytes(uint8_t *out, size_t outlen)
{
  EM_ASM({ crypto.getRandomValues(HEAPU8.subarray($0, $0 + $1)); }, out, outlen);
}
