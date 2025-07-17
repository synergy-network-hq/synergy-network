async function DilithiumModule(moduleArg = {}) {
    var moduleRtn;
    var Module = moduleArg;
    var ENVIRONMENT_IS_WEB = true;
    var ENVIRONMENT_IS_WORKER = false;
    var ENVIRONMENT_IS_NODE = false;
    var ENVIRONMENT_IS_SHELL = false;
    var arguments_ = [];
    var thisProgram = "./this.program";
    var _scriptName = import.meta.url;
    var scriptDirectory = "";
    function locateFile(path) {
        if (Module["locateFile"]) {
            return Module["locateFile"](path, scriptDirectory);
        }
        return scriptDirectory + path;
    }
    var readAsync, readBinary;
    if (ENVIRONMENT_IS_SHELL) {
        const isNode = typeof process == "object" && process.versions?.node && process.type != "renderer";
        if (isNode || typeof window == "object" || typeof WorkerGlobalScope != "undefined")
            throw new Error(
                "not compiled for this environment (did you build to HTML and try to run it not on the web, or set ENVIRONMENT to something - like node - and run it someplace else - like on the web?)"
            );
    } else if (ENVIRONMENT_IS_WEB || ENVIRONMENT_IS_WORKER) {
        try {
            scriptDirectory = new URL(".", _scriptName).href;
        } catch {}
        if (!(typeof window == "object" || typeof WorkerGlobalScope != "undefined"))
            throw new Error(
                "not compiled for this environment (did you build to HTML and try to run it not on the web, or set ENVIRONMENT to something - like node - and run it someplace else - like on the web?)"
            );
        {
            readAsync = async (url) => {
                assert(!isFileURI(url), "readAsync does not work with file:// URLs");
                var response = await fetch(url, {credentials: "same-origin"});
                if (response.ok) {
                    return response.arrayBuffer();
                }
                throw new Error(response.status + " : " + response.url);
            };
        }
    } else {
        throw new Error("environment detection error");
    }
    var out = console.log.bind(console);
    var err = console.error.bind(console);
    assert(
        !ENVIRONMENT_IS_WORKER,
        "worker environment detected but not enabled at build time.  Add `worker` to `-sENVIRONMENT` to enable."
    );
    assert(
        !ENVIRONMENT_IS_NODE,
        "node environment detected but not enabled at build time.  Add `node` to `-sENVIRONMENT` to enable."
    );
    assert(
        !ENVIRONMENT_IS_SHELL,
        "shell environment detected but not enabled at build time.  Add `shell` to `-sENVIRONMENT` to enable."
    );
    var wasmBinary;
    if (typeof WebAssembly != "object") {
        err("no native wasm support detected");
    }
    var ABORT = false;
    function assert(condition, text) {
        if (!condition) {
            abort("Assertion failed" + (text ? ": " + text : ""));
        }
    }
    var isFileURI = (filename) => filename.startsWith("file://");
    function writeStackCookie() {
        var max = _emscripten_stack_get_end();
        assert((max & 3) == 0);
        if (max == 0) {
            max += 4;
        }
        HEAPU32[max >> 2] = 34821223;
        HEAPU32[(max + 4) >> 2] = 2310721022;
        HEAPU32[0 >> 2] = 1668509029;
    }
    function checkStackCookie() {
        if (ABORT) return;
        var max = _emscripten_stack_get_end();
        if (max == 0) {
            max += 4;
        }
        var cookie1 = HEAPU32[max >> 2];
        var cookie2 = HEAPU32[(max + 4) >> 2];
        if (cookie1 != 34821223 || cookie2 != 2310721022) {
            abort(
                `Stack overflow! Stack cookie has been overwritten at ${ptrToString(
                    max
                )}, expected hex dwords 0x89BACDFE and 0x2135467, but received ${ptrToString(cookie2)} ${ptrToString(
                    cookie1
                )}`
            );
        }
        if (HEAPU32[0 >> 2] != 1668509029) {
            abort("Runtime error: The application has corrupted its heap memory area (address zero)!");
        }
    }
    var runtimeDebug = true;
    (() => {
        var h16 = new Int16Array(1);
        var h8 = new Int8Array(h16.buffer);
        h16[0] = 25459;
        if (h8[0] !== 115 || h8[1] !== 99)
            throw "Runtime error: expected the system to be little-endian! (Run with -sSUPPORT_BIG_ENDIAN to bypass)";
    })();
    function consumedModuleProp(prop) {
        if (!Object.getOwnPropertyDescriptor(Module, prop)) {
            Object.defineProperty(Module, prop, {
                configurable: true,
                set() {
                    abort(
                        `Attempt to set \`Module.${prop}\` after it has already been processed.  This can happen, for example, when code is injected via '--post-js' rather than '--pre-js'`
                    );
                },
            });
        }
    }
    function makeInvalidEarlyAccess(name) {
        return () => assert(false, `call to '${name}' via reference taken before Wasm module initialization`);
    }
    function ignoredModuleProp(prop) {
        if (Object.getOwnPropertyDescriptor(Module, prop)) {
            abort(`\`Module.${prop}\` was supplied but \`${prop}\` not included in INCOMING_MODULE_JS_API`);
        }
    }
    function isExportedByForceFilesystem(name) {
        return (
            name === "FS_createPath" ||
            name === "FS_createDataFile" ||
            name === "FS_createPreloadedFile" ||
            name === "FS_unlink" ||
            name === "addRunDependency" ||
            name === "FS_createLazyFile" ||
            name === "FS_createDevice" ||
            name === "removeRunDependency"
        );
    }
    function hookGlobalSymbolAccess(sym, func) {
        if (typeof globalThis != "undefined" && !Object.getOwnPropertyDescriptor(globalThis, sym)) {
            Object.defineProperty(globalThis, sym, {
                configurable: true,
                get() {
                    func();
                    return undefined;
                },
            });
        }
    }
    function missingGlobal(sym, msg) {
        hookGlobalSymbolAccess(sym, () => {
            warnOnce(`\`${sym}\` is not longer defined by emscripten. ${msg}`);
        });
    }
    missingGlobal("buffer", "Please use HEAP8.buffer or wasmMemory.buffer");
    missingGlobal("asm", "Please use wasmExports instead");
    function missingLibrarySymbol(sym) {
        hookGlobalSymbolAccess(sym, () => {
            var msg = `\`${sym}\` is a library symbol and not included by default; add it to your library.js __deps or to DEFAULT_LIBRARY_FUNCS_TO_INCLUDE on the command line`;
            var librarySymbol = sym;
            if (!librarySymbol.startsWith("_")) {
                librarySymbol = "$" + sym;
            }
            msg += ` (e.g. -sDEFAULT_LIBRARY_FUNCS_TO_INCLUDE='${librarySymbol}')`;
            if (isExportedByForceFilesystem(sym)) {
                msg += ". Alternatively, forcing filesystem support (-sFORCE_FILESYSTEM) can export this for you";
            }
            warnOnce(msg);
        });
        unexportedRuntimeSymbol(sym);
    }
    function unexportedRuntimeSymbol(sym) {
        if (!Object.getOwnPropertyDescriptor(Module, sym)) {
            Object.defineProperty(Module, sym, {
                configurable: true,
                get() {
                    var msg = `'${sym}' was not exported. add it to EXPORTED_RUNTIME_METHODS (see the Emscripten FAQ)`;
                    if (isExportedByForceFilesystem(sym)) {
                        msg +=
                            ". Alternatively, forcing filesystem support (-sFORCE_FILESYSTEM) can export this for you";
                    }
                    abort(msg);
                },
            });
        }
    }
    var readyPromiseResolve, readyPromiseReject;
    var wasmMemory;
    var HEAP8, HEAPU8, HEAP16, HEAPU16, HEAP32, HEAPU32, HEAPF32, HEAPF64;
    var HEAP64, HEAPU64;
    var runtimeInitialized = false;
    function updateMemoryViews() {
        var b = wasmMemory.buffer;
        HEAP8 = new Int8Array(b);
        HEAP16 = new Int16Array(b);
        Module["HEAPU8"] = HEAPU8 = new Uint8Array(b);
        HEAPU16 = new Uint16Array(b);
        HEAP32 = new Int32Array(b);
        Module["HEAPU32"] = HEAPU32 = new Uint32Array(b);
        HEAPF32 = new Float32Array(b);
        HEAPF64 = new Float64Array(b);
        HEAP64 = new BigInt64Array(b);
        HEAPU64 = new BigUint64Array(b);
    }
    assert(
        typeof Int32Array != "undefined" &&
            typeof Float64Array !== "undefined" &&
            Int32Array.prototype.subarray != undefined &&
            Int32Array.prototype.set != undefined,
        "JS engine does not provide full typed array support"
    );
    function preRun() {
        if (Module["preRun"]) {
            if (typeof Module["preRun"] == "function") Module["preRun"] = [Module["preRun"]];
            while (Module["preRun"].length) {
                addOnPreRun(Module["preRun"].shift());
            }
        }
        consumedModuleProp("preRun");
        callRuntimeCallbacks(onPreRuns);
    }
    function initRuntime() {
        assert(!runtimeInitialized);
        runtimeInitialized = true;
        checkStackCookie();
        wasmExports["__wasm_call_ctors"]();
    }
    function postRun() {
        checkStackCookie();
        if (Module["postRun"]) {
            if (typeof Module["postRun"] == "function") Module["postRun"] = [Module["postRun"]];
            while (Module["postRun"].length) {
                addOnPostRun(Module["postRun"].shift());
            }
        }
        consumedModuleProp("postRun");
        callRuntimeCallbacks(onPostRuns);
    }
    var runDependencies = 0;
    var dependenciesFulfilled = null;
    var runDependencyTracking = {};
    var runDependencyWatcher = null;
    function addRunDependency(id) {
        runDependencies++;
        Module["monitorRunDependencies"]?.(runDependencies);
        if (id) {
            assert(!runDependencyTracking[id]);
            runDependencyTracking[id] = 1;
            if (runDependencyWatcher === null && typeof setInterval != "undefined") {
                runDependencyWatcher = setInterval(() => {
                    if (ABORT) {
                        clearInterval(runDependencyWatcher);
                        runDependencyWatcher = null;
                        return;
                    }
                    var shown = false;
                    for (var dep in runDependencyTracking) {
                        if (!shown) {
                            shown = true;
                            err("still waiting on run dependencies:");
                        }
                        err(`dependency: ${dep}`);
                    }
                    if (shown) {
                        err("(end of list)");
                    }
                }, 1e4);
            }
        } else {
            err("warning: run dependency added without ID");
        }
    }
    function removeRunDependency(id) {
        runDependencies--;
        Module["monitorRunDependencies"]?.(runDependencies);
        if (id) {
            assert(runDependencyTracking[id]);
            delete runDependencyTracking[id];
        } else {
            err("warning: run dependency removed without ID");
        }
        if (runDependencies == 0) {
            if (runDependencyWatcher !== null) {
                clearInterval(runDependencyWatcher);
                runDependencyWatcher = null;
            }
            if (dependenciesFulfilled) {
                var callback = dependenciesFulfilled;
                dependenciesFulfilled = null;
                callback();
            }
        }
    }
    function abort(what) {
        Module["onAbort"]?.(what);
        what = "Aborted(" + what + ")";
        err(what);
        ABORT = true;
        var e = new WebAssembly.RuntimeError(what);
        readyPromiseReject?.(e);
        throw e;
    }
    var FS = {
        error() {
            abort(
                "Filesystem support (FS) was not included. The problem is that you are using files from JS, but files were not used from C/C++, so filesystem support was not auto-included. You can force-include filesystem support with -sFORCE_FILESYSTEM"
            );
        },
        init() {
            FS.error();
        },
        createDataFile() {
            FS.error();
        },
        createPreloadedFile() {
            FS.error();
        },
        createLazyFile() {
            FS.error();
        },
        open() {
            FS.error();
        },
        mkdev() {
            FS.error();
        },
        registerDevice() {
            FS.error();
        },
        analyzePath() {
            FS.error();
        },
        ErrnoError() {
            FS.error();
        },
    };
    function createExportWrapper(name, nargs) {
        return (...args) => {
            assert(runtimeInitialized, `native function \`${name}\` called before runtime initialization`);
            var f = wasmExports[name];
            assert(f, `exported native function \`${name}\` not found`);
            assert(
                args.length <= nargs,
                `native function \`${name}\` called with ${args.length} args but expects ${nargs}`
            );
            return f(...args);
        };
    }
    var wasmBinaryFile;
    function findWasmBinary() {
        if (Module["locateFile"]) {
            return locateFile("dilithium_wasm.wasm");
        }
        return new URL("dilithium_wasm.wasm", import.meta.url).href;
    }
    function getBinarySync(file) {
        if (file == wasmBinaryFile && wasmBinary) {
            return new Uint8Array(wasmBinary);
        }
        if (readBinary) {
            return readBinary(file);
        }
        throw "both async and sync fetching of the wasm failed";
    }
    async function getWasmBinary(binaryFile) {
        if (!wasmBinary) {
            try {
                var response = await readAsync(binaryFile);
                return new Uint8Array(response);
            } catch {}
        }
        return getBinarySync(binaryFile);
    }
    async function instantiateArrayBuffer(binaryFile, imports) {
        try {
            var binary = await getWasmBinary(binaryFile);
            var instance = await WebAssembly.instantiate(binary, imports);
            return instance;
        } catch (reason) {
            err(`failed to asynchronously prepare wasm: ${reason}`);
            if (isFileURI(wasmBinaryFile)) {
                err(
                    `warning: Loading from a file URI (${wasmBinaryFile}) is not supported in most browsers. See https://emscripten.org/docs/getting_started/FAQ.html#how-do-i-run-a-local-webserver-for-testing-why-does-my-program-stall-in-downloading-or-preparing`
                );
            }
            abort(reason);
        }
    }
    async function instantiateAsync(binary, binaryFile, imports) {
        if (!binary && typeof WebAssembly.instantiateStreaming == "function") {
            try {
                var response = fetch(binaryFile, {credentials: "same-origin"});
                var instantiationResult = await WebAssembly.instantiateStreaming(response, imports);
                return instantiationResult;
            } catch (reason) {
                err(`wasm streaming compile failed: ${reason}`);
                err("falling back to ArrayBuffer instantiation");
            }
        }
        return instantiateArrayBuffer(binaryFile, imports);
    }
    function getWasmImports() {
        return {env: wasmImports, wasi_snapshot_preview1: wasmImports};
    }
    async function createWasm() {
        function receiveInstance(instance, module) {
            wasmExports = instance.exports;
            wasmMemory = wasmExports["memory"];
            assert(wasmMemory, "memory not found in wasm exports");
            updateMemoryViews();
            assignWasmExports(wasmExports);
            removeRunDependency("wasm-instantiate");
            return wasmExports;
        }
        addRunDependency("wasm-instantiate");
        var trueModule = Module;
        function receiveInstantiationResult(result) {
            assert(
                Module === trueModule,
                "the Module object should not be replaced during async compilation - perhaps the order of HTML elements is wrong?"
            );
            trueModule = null;
            return receiveInstance(result["instance"]);
        }
        var info = getWasmImports();
        if (Module["instantiateWasm"]) {
            return new Promise((resolve, reject) => {
                try {
                    Module["instantiateWasm"](info, (mod, inst) => {
                        resolve(receiveInstance(mod, inst));
                    });
                } catch (e) {
                    err(`Module.instantiateWasm callback failed with error: ${e}`);
                    reject(e);
                }
            });
        }
        wasmBinaryFile ??= findWasmBinary();
        var result = await instantiateAsync(wasmBinary, wasmBinaryFile, info);
        var exports = receiveInstantiationResult(result);
        return exports;
    }
    class ExitStatus {
        name = "ExitStatus";
        constructor(status) {
            this.message = `Program terminated with exit(${status})`;
            this.status = status;
        }
    }
    var callRuntimeCallbacks = (callbacks) => {
        while (callbacks.length > 0) {
            callbacks.shift()(Module);
        }
    };
    var onPostRuns = [];
    var addOnPostRun = (cb) => onPostRuns.push(cb);
    var onPreRuns = [];
    var addOnPreRun = (cb) => onPreRuns.push(cb);
    function getValue(ptr, type = "i8") {
        if (type.endsWith("*")) type = "*";
        switch (type) {
            case "i1":
                return HEAP8[ptr];
            case "i8":
                return HEAP8[ptr];
            case "i16":
                return HEAP16[ptr >> 1];
            case "i32":
                return HEAP32[ptr >> 2];
            case "i64":
                return HEAP64[ptr >> 3];
            case "float":
                return HEAPF32[ptr >> 2];
            case "double":
                return HEAPF64[ptr >> 3];
            case "*":
                return HEAPU32[ptr >> 2];
            default:
                abort(`invalid type for getValue: ${type}`);
        }
    }
    var noExitRuntime = true;
    var ptrToString = (ptr) => {
        assert(typeof ptr === "number");
        ptr >>>= 0;
        return "0x" + ptr.toString(16).padStart(8, "0");
    };
    function setValue(ptr, value, type = "i8") {
        if (type.endsWith("*")) type = "*";
        switch (type) {
            case "i1":
                HEAP8[ptr] = value;
                break;
            case "i8":
                HEAP8[ptr] = value;
                break;
            case "i16":
                HEAP16[ptr >> 1] = value;
                break;
            case "i32":
                HEAP32[ptr >> 2] = value;
                break;
            case "i64":
                HEAP64[ptr >> 3] = BigInt(value);
                break;
            case "float":
                HEAPF32[ptr >> 2] = value;
                break;
            case "double":
                HEAPF64[ptr >> 3] = value;
                break;
            case "*":
                HEAPU32[ptr >> 2] = value;
                break;
            default:
                abort(`invalid type for setValue: ${type}`);
        }
    }
    var stackRestore = (val) => __emscripten_stack_restore(val);
    var stackSave = () => _emscripten_stack_get_current();
    var warnOnce = (text) => {
        warnOnce.shown ||= {};
        if (!warnOnce.shown[text]) {
            warnOnce.shown[text] = 1;
            err(text);
        }
    };
    var __abort_js = () => abort("native code called abort()");
    var readEmAsmArgsArray = [];
    var readEmAsmArgs = (sigPtr, buf) => {
        assert(Array.isArray(readEmAsmArgsArray));
        assert(buf % 16 == 0);
        readEmAsmArgsArray.length = 0;
        var ch;
        while ((ch = HEAPU8[sigPtr++])) {
            var chr = String.fromCharCode(ch);
            var validChars = ["d", "f", "i", "p"];
            validChars.push("j");
            assert(
                validChars.includes(chr),
                `Invalid character ${ch}("${chr}") in readEmAsmArgs! Use only [${validChars}], and do not specify "v" for void return argument.`
            );
            var wide = ch != 105;
            wide &= ch != 112;
            buf += wide && buf % 8 ? 4 : 0;
            readEmAsmArgsArray.push(
                ch == 112
                    ? HEAPU32[buf >> 2]
                    : ch == 106
                    ? HEAP64[buf >> 3]
                    : ch == 105
                    ? HEAP32[buf >> 2]
                    : HEAPF64[buf >> 3]
            );
            buf += wide ? 8 : 4;
        }
        return readEmAsmArgsArray;
    };
    var runEmAsmFunction = (code, sigPtr, argbuf) => {
        var args = readEmAsmArgs(sigPtr, argbuf);
        assert(
            ASM_CONSTS.hasOwnProperty(code),
            `No EM_ASM constant found at address ${code}.  The loaded WebAssembly file is likely out of sync with the generated JavaScript.`
        );
        return ASM_CONSTS[code](...args);
    };
    var _emscripten_asm_const_int = (code, sigPtr, argbuf) => runEmAsmFunction(code, sigPtr, argbuf);
    var getHeapMax = () => 2147483648;
    var alignMemory = (size, alignment) => {
        assert(alignment, "alignment argument is required");
        return Math.ceil(size / alignment) * alignment;
    };
    var growMemory = (size) => {
        var oldHeapSize = wasmMemory.buffer.byteLength;
        var pages = ((size - oldHeapSize + 65535) / 65536) | 0;
        try {
            wasmMemory.grow(pages);
            updateMemoryViews();
            return 1;
        } catch (e) {
            err(`growMemory: Attempted to grow heap from ${oldHeapSize} bytes to ${size} bytes, but got error: ${e}`);
        }
    };
    var _emscripten_resize_heap = (requestedSize) => {
        var oldSize = HEAPU8.length;
        requestedSize >>>= 0;
        assert(requestedSize > oldSize);
        var maxHeapSize = getHeapMax();
        if (requestedSize > maxHeapSize) {
            err(`Cannot enlarge memory, requested ${requestedSize} bytes, but the limit is ${maxHeapSize} bytes!`);
            return false;
        }
        for (var cutDown = 1; cutDown <= 4; cutDown *= 2) {
            var overGrownHeapSize = oldSize * (1 + 0.2 / cutDown);
            overGrownHeapSize = Math.min(overGrownHeapSize, requestedSize + 100663296);
            var newSize = Math.min(maxHeapSize, alignMemory(Math.max(requestedSize, overGrownHeapSize), 65536));
            var replacement = growMemory(newSize);
            if (replacement) {
                return true;
            }
        }
        err(`Failed to grow the heap from ${oldSize} bytes to ${newSize} bytes, not enough memory!`);
        return false;
    };
    var UTF8Decoder = typeof TextDecoder != "undefined" ? new TextDecoder() : undefined;
    var findStringEnd = (heapOrArray, idx, maxBytesToRead, ignoreNul) => {
        var maxIdx = idx + maxBytesToRead;
        if (ignoreNul) return maxIdx;
        while (heapOrArray[idx] && !(idx >= maxIdx)) ++idx;
        return idx;
    };
    var UTF8ArrayToString = (heapOrArray, idx = 0, maxBytesToRead, ignoreNul) => {
        var endPtr = findStringEnd(heapOrArray, idx, maxBytesToRead, ignoreNul);
        if (endPtr - idx > 16 && heapOrArray.buffer && UTF8Decoder) {
            return UTF8Decoder.decode(heapOrArray.subarray(idx, endPtr));
        }
        var str = "";
        while (idx < endPtr) {
            var u0 = heapOrArray[idx++];
            if (!(u0 & 128)) {
                str += String.fromCharCode(u0);
                continue;
            }
            var u1 = heapOrArray[idx++] & 63;
            if ((u0 & 224) == 192) {
                str += String.fromCharCode(((u0 & 31) << 6) | u1);
                continue;
            }
            var u2 = heapOrArray[idx++] & 63;
            if ((u0 & 240) == 224) {
                u0 = ((u0 & 15) << 12) | (u1 << 6) | u2;
            } else {
                if ((u0 & 248) != 240)
                    warnOnce(
                        "Invalid UTF-8 leading byte " +
                            ptrToString(u0) +
                            " encountered when deserializing a UTF-8 string in wasm memory to a JS string!"
                    );
                u0 = ((u0 & 7) << 18) | (u1 << 12) | (u2 << 6) | (heapOrArray[idx++] & 63);
            }
            if (u0 < 65536) {
                str += String.fromCharCode(u0);
            } else {
                var ch = u0 - 65536;
                str += String.fromCharCode(55296 | (ch >> 10), 56320 | (ch & 1023));
            }
        }
        return str;
    };
    var UTF8ToString = (ptr, maxBytesToRead, ignoreNul) => {
        assert(typeof ptr == "number", `UTF8ToString expects a number (got ${typeof ptr})`);
        return ptr ? UTF8ArrayToString(HEAPU8, ptr, maxBytesToRead, ignoreNul) : "";
    };
    var _fd_close = (fd) => {
        abort("fd_close called without SYSCALLS_REQUIRE_FILESYSTEM");
    };
    var INT53_MAX = 9007199254740992;
    var INT53_MIN = -9007199254740992;
    var bigintToI53Checked = (num) => (num < INT53_MIN || num > INT53_MAX ? NaN : Number(num));
    function _fd_seek(fd, offset, whence, newOffset) {
        offset = bigintToI53Checked(offset);
        return 70;
    }
    var printCharBuffers = [null, [], []];
    var printChar = (stream, curr) => {
        var buffer = printCharBuffers[stream];
        assert(buffer);
        if (curr === 0 || curr === 10) {
            (stream === 1 ? out : err)(UTF8ArrayToString(buffer));
            buffer.length = 0;
        } else {
            buffer.push(curr);
        }
    };
    var flush_NO_FILESYSTEM = () => {
        _fflush(0);
        if (printCharBuffers[1].length) printChar(1, 10);
        if (printCharBuffers[2].length) printChar(2, 10);
    };
    var _fd_write = (fd, iov, iovcnt, pnum) => {
        var num = 0;
        for (var i = 0; i < iovcnt; i++) {
            var ptr = HEAPU32[iov >> 2];
            var len = HEAPU32[(iov + 4) >> 2];
            iov += 8;
            for (var j = 0; j < len; j++) {
                printChar(fd, HEAPU8[ptr + j]);
            }
            num += len;
        }
        HEAPU32[pnum >> 2] = num;
        return 0;
    };
    var getCFunc = (ident) => {
        var func = Module["_" + ident];
        assert(func, "Cannot call unknown function " + ident + ", make sure it is exported");
        return func;
    };
    var writeArrayToMemory = (array, buffer) => {
        assert(array.length >= 0, "writeArrayToMemory array must have a length (should be an array or typed array)");
        HEAP8.set(array, buffer);
    };
    var lengthBytesUTF8 = (str) => {
        var len = 0;
        for (var i = 0; i < str.length; ++i) {
            var c = str.charCodeAt(i);
            if (c <= 127) {
                len++;
            } else if (c <= 2047) {
                len += 2;
            } else if (c >= 55296 && c <= 57343) {
                len += 4;
                ++i;
            } else {
                len += 3;
            }
        }
        return len;
    };
    var stringToUTF8Array = (str, heap, outIdx, maxBytesToWrite) => {
        assert(typeof str === "string", `stringToUTF8Array expects a string (got ${typeof str})`);
        if (!(maxBytesToWrite > 0)) return 0;
        var startIdx = outIdx;
        var endIdx = outIdx + maxBytesToWrite - 1;
        for (var i = 0; i < str.length; ++i) {
            var u = str.codePointAt(i);
            if (u <= 127) {
                if (outIdx >= endIdx) break;
                heap[outIdx++] = u;
            } else if (u <= 2047) {
                if (outIdx + 1 >= endIdx) break;
                heap[outIdx++] = 192 | (u >> 6);
                heap[outIdx++] = 128 | (u & 63);
            } else if (u <= 65535) {
                if (outIdx + 2 >= endIdx) break;
                heap[outIdx++] = 224 | (u >> 12);
                heap[outIdx++] = 128 | ((u >> 6) & 63);
                heap[outIdx++] = 128 | (u & 63);
            } else {
                if (outIdx + 3 >= endIdx) break;
                if (u > 1114111)
                    warnOnce(
                        "Invalid Unicode code point " +
                            ptrToString(u) +
                            " encountered when serializing a JS string to a UTF-8 string in wasm memory! (Valid unicode code points should be in range 0-0x10FFFF)."
                    );
                heap[outIdx++] = 240 | (u >> 18);
                heap[outIdx++] = 128 | ((u >> 12) & 63);
                heap[outIdx++] = 128 | ((u >> 6) & 63);
                heap[outIdx++] = 128 | (u & 63);
                i++;
            }
        }
        heap[outIdx] = 0;
        return outIdx - startIdx;
    };
    var stringToUTF8 = (str, outPtr, maxBytesToWrite) => {
        assert(
            typeof maxBytesToWrite == "number",
            "stringToUTF8(str, outPtr, maxBytesToWrite) is missing the third parameter that specifies the length of the output buffer!"
        );
        return stringToUTF8Array(str, HEAPU8, outPtr, maxBytesToWrite);
    };
    var stackAlloc = (sz) => __emscripten_stack_alloc(sz);
    var stringToUTF8OnStack = (str) => {
        var size = lengthBytesUTF8(str) + 1;
        var ret = stackAlloc(size);
        stringToUTF8(str, ret, size);
        return ret;
    };
    var ccall = (ident, returnType, argTypes, args, opts) => {
        var toC = {
            string: (str) => {
                var ret = 0;
                if (str !== null && str !== undefined && str !== 0) {
                    ret = stringToUTF8OnStack(str);
                }
                return ret;
            },
            array: (arr) => {
                var ret = stackAlloc(arr.length);
                writeArrayToMemory(arr, ret);
                return ret;
            },
        };
        function convertReturnValue(ret) {
            if (returnType === "string") {
                return UTF8ToString(ret);
            }
            if (returnType === "boolean") return Boolean(ret);
            return ret;
        }
        var func = getCFunc(ident);
        var cArgs = [];
        var stack = 0;
        assert(returnType !== "array", 'Return type should not be "array".');
        if (args) {
            for (var i = 0; i < args.length; i++) {
                var converter = toC[argTypes[i]];
                if (converter) {
                    if (stack === 0) stack = stackSave();
                    cArgs[i] = converter(args[i]);
                } else {
                    cArgs[i] = args[i];
                }
            }
        }
        var ret = func(...cArgs);
        function onDone(ret) {
            if (stack !== 0) stackRestore(stack);
            return convertReturnValue(ret);
        }
        ret = onDone(ret);
        return ret;
    };
    var cwrap =
        (ident, returnType, argTypes, opts) =>
        (...args) =>
            ccall(ident, returnType, argTypes, args, opts);
    {
        if (Module["noExitRuntime"]) noExitRuntime = Module["noExitRuntime"];
        if (Module["print"]) out = Module["print"];
        if (Module["printErr"]) err = Module["printErr"];
        if (Module["wasmBinary"]) wasmBinary = Module["wasmBinary"];
        Module["FS_createDataFile"] = FS.createDataFile;
        Module["FS_createPreloadedFile"] = FS.createPreloadedFile;
        checkIncomingModuleAPI();
        if (Module["arguments"]) arguments_ = Module["arguments"];
        if (Module["thisProgram"]) thisProgram = Module["thisProgram"];
        assert(
            typeof Module["memoryInitializerPrefixURL"] == "undefined",
            "Module.memoryInitializerPrefixURL option was removed, use Module.locateFile instead"
        );
        assert(
            typeof Module["pthreadMainPrefixURL"] == "undefined",
            "Module.pthreadMainPrefixURL option was removed, use Module.locateFile instead"
        );
        assert(
            typeof Module["cdInitializerPrefixURL"] == "undefined",
            "Module.cdInitializerPrefixURL option was removed, use Module.locateFile instead"
        );
        assert(
            typeof Module["filePackagePrefixURL"] == "undefined",
            "Module.filePackagePrefixURL option was removed, use Module.locateFile instead"
        );
        assert(typeof Module["read"] == "undefined", "Module.read option was removed");
        assert(
            typeof Module["readAsync"] == "undefined",
            "Module.readAsync option was removed (modify readAsync in JS)"
        );
        assert(
            typeof Module["readBinary"] == "undefined",
            "Module.readBinary option was removed (modify readBinary in JS)"
        );
        assert(
            typeof Module["setWindowTitle"] == "undefined",
            "Module.setWindowTitle option was removed (modify emscripten_set_window_title in JS)"
        );
        assert(
            typeof Module["TOTAL_MEMORY"] == "undefined",
            "Module.TOTAL_MEMORY has been renamed Module.INITIAL_MEMORY"
        );
        assert(
            typeof Module["ENVIRONMENT"] == "undefined",
            "Module.ENVIRONMENT has been deprecated. To force the environment, use the ENVIRONMENT compile-time option (for example, -sENVIRONMENT=web or -sENVIRONMENT=node)"
        );
        assert(
            typeof Module["STACK_SIZE"] == "undefined",
            "STACK_SIZE can no longer be set at runtime.  Use -sSTACK_SIZE at link time"
        );
        assert(
            typeof Module["wasmMemory"] == "undefined",
            "Use of `wasmMemory` detected.  Use -sIMPORTED_MEMORY to define wasmMemory externally"
        );
        assert(
            typeof Module["INITIAL_MEMORY"] == "undefined",
            "Detected runtime INITIAL_MEMORY setting.  Use -sIMPORTED_MEMORY to define wasmMemory dynamically"
        );
    }
    Module["ccall"] = ccall;
    Module["cwrap"] = cwrap;
    Module["setValue"] = setValue;
    Module["getValue"] = getValue;
    Module["UTF8ToString"] = UTF8ToString;
    Module["stringToUTF8"] = stringToUTF8;
    var missingLibrarySymbols = [
        "writeI53ToI64",
        "writeI53ToI64Clamped",
        "writeI53ToI64Signaling",
        "writeI53ToU64Clamped",
        "writeI53ToU64Signaling",
        "readI53FromI64",
        "readI53FromU64",
        "convertI32PairToI53",
        "convertI32PairToI53Checked",
        "convertU32PairToI53",
        "getTempRet0",
        "setTempRet0",
        "zeroMemory",
        "exitJS",
        "withStackSave",
        "strError",
        "inetPton4",
        "inetNtop4",
        "inetPton6",
        "inetNtop6",
        "readSockaddr",
        "writeSockaddr",
        "runMainThreadEmAsm",
        "jstoi_q",
        "getExecutableName",
        "autoResumeAudioContext",
        "getDynCaller",
        "dynCall",
        "handleException",
        "keepRuntimeAlive",
        "runtimeKeepalivePush",
        "runtimeKeepalivePop",
        "callUserCallback",
        "maybeExit",
        "asmjsMangle",
        "asyncLoad",
        "mmapAlloc",
        "HandleAllocator",
        "getNativeTypeSize",
        "getUniqueRunDependency",
        "addOnInit",
        "addOnPostCtor",
        "addOnPreMain",
        "addOnExit",
        "STACK_SIZE",
        "STACK_ALIGN",
        "POINTER_SIZE",
        "ASSERTIONS",
        "convertJsFunctionToWasm",
        "getEmptyTableSlot",
        "updateTableMap",
        "getFunctionAddress",
        "addFunction",
        "removeFunction",
        "intArrayFromString",
        "intArrayToString",
        "AsciiToString",
        "stringToAscii",
        "UTF16ToString",
        "stringToUTF16",
        "lengthBytesUTF16",
        "UTF32ToString",
        "stringToUTF32",
        "lengthBytesUTF32",
        "stringToNewUTF8",
        "registerKeyEventCallback",
        "maybeCStringToJsString",
        "findEventTarget",
        "getBoundingClientRect",
        "fillMouseEventData",
        "registerMouseEventCallback",
        "registerWheelEventCallback",
        "registerUiEventCallback",
        "registerFocusEventCallback",
        "fillDeviceOrientationEventData",
        "registerDeviceOrientationEventCallback",
        "fillDeviceMotionEventData",
        "registerDeviceMotionEventCallback",
        "screenOrientation",
        "fillOrientationChangeEventData",
        "registerOrientationChangeEventCallback",
        "fillFullscreenChangeEventData",
        "registerFullscreenChangeEventCallback",
        "JSEvents_requestFullscreen",
        "JSEvents_resizeCanvasForFullscreen",
        "registerRestoreOldStyle",
        "hideEverythingExceptGivenElement",
        "restoreHiddenElements",
        "setLetterbox",
        "softFullscreenResizeWebGLRenderTarget",
        "doRequestFullscreen",
        "fillPointerlockChangeEventData",
        "registerPointerlockChangeEventCallback",
        "registerPointerlockErrorEventCallback",
        "requestPointerLock",
        "fillVisibilityChangeEventData",
        "registerVisibilityChangeEventCallback",
        "registerTouchEventCallback",
        "fillGamepadEventData",
        "registerGamepadEventCallback",
        "registerBeforeUnloadEventCallback",
        "fillBatteryEventData",
        "registerBatteryEventCallback",
        "setCanvasElementSize",
        "getCanvasElementSize",
        "jsStackTrace",
        "getCallstack",
        "convertPCtoSourceLocation",
        "getEnvStrings",
        "checkWasiClock",
        "wasiRightsToMuslOFlags",
        "wasiOFlagsToMuslOFlags",
        "initRandomFill",
        "randomFill",
        "safeSetTimeout",
        "setImmediateWrapped",
        "safeRequestAnimationFrame",
        "clearImmediateWrapped",
        "registerPostMainLoop",
        "registerPreMainLoop",
        "getPromise",
        "makePromise",
        "idsToPromises",
        "makePromiseCallback",
        "ExceptionInfo",
        "findMatchingCatch",
        "Browser_asyncPrepareDataCounter",
        "isLeapYear",
        "ydayFromDate",
        "arraySum",
        "addDays",
        "getSocketFromFD",
        "getSocketAddress",
        "heapObjectForWebGLType",
        "toTypedArrayIndex",
        "webgl_enable_ANGLE_instanced_arrays",
        "webgl_enable_OES_vertex_array_object",
        "webgl_enable_WEBGL_draw_buffers",
        "webgl_enable_WEBGL_multi_draw",
        "webgl_enable_EXT_polygon_offset_clamp",
        "webgl_enable_EXT_clip_control",
        "webgl_enable_WEBGL_polygon_mode",
        "emscriptenWebGLGet",
        "computeUnpackAlignedImageSize",
        "colorChannelsInGlTextureFormat",
        "emscriptenWebGLGetTexPixelData",
        "emscriptenWebGLGetUniform",
        "webglGetUniformLocation",
        "webglPrepareUniformLocationsBeforeFirstUse",
        "webglGetLeftBracePos",
        "emscriptenWebGLGetVertexAttrib",
        "__glGetActiveAttribOrUniform",
        "writeGLArray",
        "registerWebGlEventCallback",
        "runAndAbortIfError",
        "ALLOC_NORMAL",
        "ALLOC_STACK",
        "allocate",
        "writeStringToMemory",
        "writeAsciiToMemory",
        "demangle",
        "stackTrace",
    ];
    missingLibrarySymbols.forEach(missingLibrarySymbol);
    var unexportedSymbols = [
        "run",
        "addRunDependency",
        "removeRunDependency",
        "out",
        "err",
        "callMain",
        "abort",
        "wasmMemory",
        "wasmExports",
        "HEAPF32",
        "HEAPF64",
        "HEAP8",
        "HEAP16",
        "HEAPU16",
        "HEAP32",
        "HEAP64",
        "HEAPU64",
        "writeStackCookie",
        "checkStackCookie",
        "INT53_MAX",
        "INT53_MIN",
        "bigintToI53Checked",
        "stackSave",
        "stackRestore",
        "stackAlloc",
        "ptrToString",
        "getHeapMax",
        "growMemory",
        "ENV",
        "ERRNO_CODES",
        "DNS",
        "Protocols",
        "Sockets",
        "timers",
        "warnOnce",
        "readEmAsmArgsArray",
        "readEmAsmArgs",
        "runEmAsmFunction",
        "alignMemory",
        "wasmTable",
        "noExitRuntime",
        "addOnPreRun",
        "addOnPostRun",
        "freeTableIndexes",
        "functionsInTableMap",
        "PATH",
        "PATH_FS",
        "UTF8Decoder",
        "UTF8ArrayToString",
        "stringToUTF8Array",
        "lengthBytesUTF8",
        "UTF16Decoder",
        "stringToUTF8OnStack",
        "writeArrayToMemory",
        "JSEvents",
        "specialHTMLTargets",
        "findCanvasEventTarget",
        "currentFullscreenStrategy",
        "restoreOldWindowedStyle",
        "UNWIND_CACHE",
        "ExitStatus",
        "flush_NO_FILESYSTEM",
        "emSetImmediate",
        "emClearImmediate_deps",
        "emClearImmediate",
        "promiseMap",
        "uncaughtExceptionCount",
        "exceptionLast",
        "exceptionCaught",
        "Browser",
        "requestFullscreen",
        "requestFullScreen",
        "setCanvasSize",
        "getUserMedia",
        "createContext",
        "getPreloadedImageData__data",
        "wget",
        "MONTH_DAYS_REGULAR",
        "MONTH_DAYS_LEAP",
        "MONTH_DAYS_REGULAR_CUMULATIVE",
        "MONTH_DAYS_LEAP_CUMULATIVE",
        "SYSCALLS",
        "tempFixedLengthArray",
        "miniTempWebGLFloatBuffers",
        "miniTempWebGLIntBuffers",
        "GL",
        "AL",
        "GLUT",
        "EGL",
        "GLEW",
        "IDBStore",
        "SDL",
        "SDL_gfx",
        "allocateUTF8",
        "allocateUTF8OnStack",
        "print",
        "printErr",
        "jstoi_s",
    ];
    unexportedSymbols.forEach(unexportedRuntimeSymbol);
    function checkIncomingModuleAPI() {
        ignoredModuleProp("fetchSettings");
    }
    var ASM_CONSTS = {
        2396: ($0, $1) => {
            crypto.getRandomValues(HEAPU8.subarray($0, $0 + $1));
        },
    };
    var _dilithium3_keypair = (Module["_dilithium3_keypair"] = makeInvalidEarlyAccess("_dilithium3_keypair"));
    var _dilithium3_sign = (Module["_dilithium3_sign"] = makeInvalidEarlyAccess("_dilithium3_sign"));
    var _dilithium3_verify = (Module["_dilithium3_verify"] = makeInvalidEarlyAccess("_dilithium3_verify"));
    var _fflush = makeInvalidEarlyAccess("_fflush");
    var _malloc = (Module["_malloc"] = makeInvalidEarlyAccess("_malloc"));
    var _free = (Module["_free"] = makeInvalidEarlyAccess("_free"));
    var _emscripten_stack_init = makeInvalidEarlyAccess("_emscripten_stack_init");
    var _emscripten_stack_get_free = makeInvalidEarlyAccess("_emscripten_stack_get_free");
    var _emscripten_stack_get_base = makeInvalidEarlyAccess("_emscripten_stack_get_base");
    var _emscripten_stack_get_end = makeInvalidEarlyAccess("_emscripten_stack_get_end");
    var __emscripten_stack_restore = makeInvalidEarlyAccess("__emscripten_stack_restore");
    var __emscripten_stack_alloc = makeInvalidEarlyAccess("__emscripten_stack_alloc");
    var _emscripten_stack_get_current = makeInvalidEarlyAccess("_emscripten_stack_get_current");
    function assignWasmExports(wasmExports) {
        Module["_dilithium3_keypair"] = _dilithium3_keypair = createExportWrapper("dilithium3_keypair", 2);
        Module["_dilithium3_sign"] = _dilithium3_sign = createExportWrapper("dilithium3_sign", 5);
        Module["_dilithium3_verify"] = _dilithium3_verify = createExportWrapper("dilithium3_verify", 5);
        _fflush = createExportWrapper("fflush", 1);
        Module["_malloc"] = _malloc = createExportWrapper("malloc", 1);
        Module["_free"] = _free = createExportWrapper("free", 1);
        _emscripten_stack_init = wasmExports["emscripten_stack_init"];
        _emscripten_stack_get_free = wasmExports["emscripten_stack_get_free"];
        _emscripten_stack_get_base = wasmExports["emscripten_stack_get_base"];
        _emscripten_stack_get_end = wasmExports["emscripten_stack_get_end"];
        __emscripten_stack_restore = wasmExports["_emscripten_stack_restore"];
        __emscripten_stack_alloc = wasmExports["_emscripten_stack_alloc"];
        _emscripten_stack_get_current = wasmExports["emscripten_stack_get_current"];
    }
    var wasmImports = {
        _abort_js: __abort_js,
        emscripten_asm_const_int: _emscripten_asm_const_int,
        emscripten_resize_heap: _emscripten_resize_heap,
        fd_close: _fd_close,
        fd_seek: _fd_seek,
        fd_write: _fd_write,
    };
    var wasmExports = await createWasm();
    var calledRun;
    function stackCheckInit() {
        _emscripten_stack_init();
        writeStackCookie();
    }
    function run() {
        if (runDependencies > 0) {
            dependenciesFulfilled = run;
            return;
        }
        stackCheckInit();
        preRun();
        if (runDependencies > 0) {
            dependenciesFulfilled = run;
            return;
        }
        function doRun() {
            assert(!calledRun);
            calledRun = true;
            Module["calledRun"] = true;
            if (ABORT) return;
            initRuntime();
            readyPromiseResolve?.(Module);
            Module["onRuntimeInitialized"]?.();
            consumedModuleProp("onRuntimeInitialized");
            assert(
                !Module["_main"],
                'compiled without a main, but one is present. if you added it from JS, use Module["onRuntimeInitialized"]'
            );
            postRun();
        }
        if (Module["setStatus"]) {
            Module["setStatus"]("Running...");
            setTimeout(() => {
                setTimeout(() => Module["setStatus"](""), 1);
                doRun();
            }, 1);
        } else {
            doRun();
        }
        checkStackCookie();
    }
    function preInit() {
        if (Module["preInit"]) {
            if (typeof Module["preInit"] == "function") Module["preInit"] = [Module["preInit"]];
            while (Module["preInit"].length > 0) {
                Module["preInit"].shift()();
            }
        }
        consumedModuleProp("preInit");
    }
    preInit();
    run();
    if (runtimeInitialized) {
        moduleRtn = Module;
    } else {
        moduleRtn = new Promise((resolve, reject) => {
            readyPromiseResolve = resolve;
            readyPromiseReject = reject;
        });
    }
    for (const prop of Object.keys(Module)) {
        if (!(prop in moduleArg)) {
            Object.defineProperty(moduleArg, prop, {
                configurable: true,
                get() {
                    abort(
                        `Access to module property ('${prop}') is no longer possible via the module constructor argument; Instead, use the result of the module constructor.`
                    );
                },
            });
        }
    }
    return moduleRtn;
}
export default DilithiumModule;
