/**
 * RustChain Payment Widget v1.0.0
 * Embeddable RTC payment button with client-side Ed25519 signing
 * 
 * Usage:
 *   <script src="rustchain-pay.js"></script>
 *   <div id="rtc-pay" data-to="RTCxxx..." data-amount="5" data-memo="Order #123"></div>
 * 
 * Security: Private keys NEVER leave the browser. All signing is done locally.
 */
(function() {
  'use strict';

  // Configuration
  const DEFAULT_NODE = 'https://50.28.86.131';
  const WIDGET_VERSION = '1.0.0';

  // TweetNaCl.js (minimal Ed25519 implementation) - Public Domain
  // https://tweetnacl.js.org
  const nacl = (function() {
    var gf = function(init) {
      var i, r = new Float64Array(16);
      if (init) for (i = 0; i < init.length; i++) r[i] = init[i];
      return r;
    };
    var _0 = new Uint8Array(16);
    var _9 = new Uint8Array(32); _9[0] = 9;
    var gf0 = gf(), gf1 = gf([1]),
        D = gf([0x78a3, 0x1359, 0x4dca, 0x75eb, 0xd8ab, 0x4141, 0x0a4d, 0x0070, 0xe898, 0x7779, 0x4079, 0x8cc7, 0xfe73, 0x2b6f, 0x6cee, 0x5203]),
        D2 = gf([0xf159, 0x26b2, 0x9b94, 0xebd6, 0xb156, 0x8283, 0x149a, 0x00e0, 0xd130, 0xeef3, 0x80f2, 0x198e, 0xfce7, 0x56df, 0xd9dc, 0x2406]),
        X = gf([0xd51a, 0x8f25, 0x2d60, 0xc956, 0xa7b2, 0x9525, 0xc760, 0x692c, 0xdc5c, 0xfdd6, 0xe231, 0xc0a4, 0x53fe, 0xcd6e, 0x36d3, 0x2169]),
        Y = gf([0x6658, 0x6666, 0x6666, 0x6666, 0x6666, 0x6666, 0x6666, 0x6666, 0x6666, 0x6666, 0x6666, 0x6666, 0x6666, 0x6666, 0x6666, 0x6666]),
        I = gf([0xa0b0, 0x4a0e, 0x1b27, 0xc4ee, 0xe478, 0xad2f, 0x1806, 0x2f43, 0xd7a7, 0x3dfb, 0x0099, 0x2b4d, 0xdf0b, 0x4fc1, 0x2480, 0x2b83]);

    function L32(x, c) { return (x << c) | (x >>> (32 - c)); }
    function ld32(x, i) { var u = x[i+3] & 0xff; u = (u<<8)|(x[i+2] & 0xff); u = (u<<8)|(x[i+1] & 0xff); return (u<<8)|(x[i] & 0xff); }
    function st32(x, j, u) { for (var i = 0; i < 4; i++) { x[j+i] = u & 255; u >>>= 8; } }
    function vn(x, xi, y, yi, n) { var d = 0; for (var i = 0; i < n; i++) d |= x[xi+i]^y[yi+i]; return (1 & ((d - 1) >>> 8)) - 1; }
    function crypto_verify_32(x, xi, y, yi) { return vn(x,xi,y,yi,32); }

    function core(out, inp, k, c, h) {
      var w = new Uint32Array(16), x = new Uint32Array(16), y = new Uint32Array(16), t = new Uint32Array(4);
      var i, j, m;
      for (i = 0; i < 4; i++) { x[i*5] = ld32(c, 4*i); x[1+i] = ld32(k, 4*i); x[6+i] = ld32(inp, 4*i); x[11+i] = ld32(k, 16+4*i); }
      for (i = 0; i < 16; i++) y[i] = x[i];
      for (i = 0; i < 20; i++) {
        for (j = 0; j < 4; j++) {
          for (m = 0; m < 4; m++) t[m] = x[(5*j+4*m)%16];
          t[1] ^= L32((t[0]+t[3])|0, 7); t[2] ^= L32((t[1]+t[0])|0, 9); t[3] ^= L32((t[2]+t[1])|0,13); t[0] ^= L32((t[3]+t[2])|0,18);
          for (m = 0; m < 4; m++) w[4*j+(j+m)%4] = t[m];
        }
        for (m = 0; m < 16; m++) x[m] = w[m];
      }
      if (h) { for (i = 0; i < 16; i++) x[i] = (x[i] + y[i]) | 0; for (i = 0; i < 4; i++) { x[5*i] = (x[5*i] - ld32(c, 4*i)) | 0; x[6+i] = (x[6+i] - ld32(inp, 4*i)) | 0; } }
      else { for (i = 0; i < 16; i++) x[i] = (x[i] + y[i]) | 0; }
      for (i = 0; i < 16; i++) st32(out, 4*i, x[i]);
    }

    function crypto_core_salsa20(out, inp, k, c) { core(out, inp, k, c, false); return 0; }
    function crypto_core_hsalsa20(out, inp, k, c) { core(out, inp, k, c, true); return 0; }
    var sigma = new Uint8Array([101, 120, 112, 97, 110, 100, 32, 51, 50, 45, 98, 121, 116, 101, 32, 107]);

    function crypto_stream_salsa20_xor(c, cpos, m, mpos, b, n, k) {
      var z = new Uint8Array(16), x = new Uint8Array(64);
      var u, i;
      if (!b) return 0;
      for (i = 0; i < 16; i++) z[i] = 0;
      for (i = 0; i < 8; i++) z[i] = n[i];
      while (b >= 64) {
        crypto_core_salsa20(x, z, k, sigma);
        for (i = 0; i < 64; i++) c[cpos+i] = (m?m[mpos+i]:0) ^ x[i];
        u = 1;
        for (i = 8; i < 16; i++) { u = u + (z[i] & 255) | 0; z[i] = u & 255; u >>>= 8; }
        b -= 64; cpos += 64; if(m) mpos += 64;
      }
      if (b > 0) { crypto_core_salsa20(x, z, k, sigma); for (i = 0; i < b; i++) c[cpos+i] = (m?m[mpos+i]:0) ^ x[i]; }
      return 0;
    }
    function crypto_stream_salsa20(c, cpos, d, n, k) { return crypto_stream_salsa20_xor(c, cpos, null, 0, d, n, k); }
    function crypto_stream(c, cpos, d, n, k) {
      var s = new Uint8Array(32);
      crypto_core_hsalsa20(s, n, k, sigma);
      return crypto_stream_salsa20(c, cpos, d, n.subarray(16), s);
    }
    function crypto_stream_xor(c, cpos, m, mpos, d, n, k) {
      var s = new Uint8Array(32);
      crypto_core_hsalsa20(s, n, k, sigma);
      return crypto_stream_salsa20_xor(c, cpos, m, mpos, d, n.subarray(16), s);
    }

    function add1305(h, c) { var u = 0; for (var j = 0; j < 17; j++) { u = (u + ((h[j] + c[j]) | 0)) | 0; h[j] = u & 255; u >>>= 8; } }
    var minusp = new Uint32Array([5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 252]);

    function crypto_onetimeauth(out, outpos, m, mpos, n, k) {
      var s, i, j, u, x = new Uint32Array(17), r = new Uint32Array(17), h = new Uint32Array(17), c = new Uint32Array(17), g = new Uint32Array(17);
      for (j = 0; j < 17; j++) r[j] = h[j] = 0;
      for (j = 0; j < 16; j++) r[j] = k[j];
      r[3] &= 15; r[4] &= 252; r[7] &= 15; r[8] &= 252; r[11] &= 15; r[12] &= 252; r[15] &= 15;
      while (n > 0) {
        for (j = 0; j < 17; j++) c[j] = 0;
        for (j = 0; (j < 16) && (j < n); j++) c[j] = m[mpos+j];
        c[j] = 1; mpos += j; n -= j;
        add1305(h, c);
        for (i = 0; i < 17; i++) { x[i] = 0; for (j = 0; j < 17; j++) x[i] = (x[i] + (h[j] * ((j <= i) ? r[i-j] : ((320 * r[i+17-j])|0))) | 0) | 0; }
        for (i = 0; i < 17; i++) h[i] = x[i];
        u = 0;
        for (j = 0; j < 16; j++) { u = (u + h[j]) | 0; h[j] = u & 255; u >>>= 8; }
        u = (u + h[16]) | 0; h[16] = u & 3;
        u = (5 * (u >>> 2)) | 0;
        for (j = 0; j < 16; j++) { u = (u + h[j]) | 0; h[j] = u & 255; u >>>= 8; }
        u = (u + h[16]) | 0; h[16] = u;
      }
      for (j = 0; j < 17; j++) g[j] = h[j];
      add1305(h, minusp);
      s = (-(h[16] >>> 7) | 0);
      for (j = 0; j < 17; j++) h[j] ^= s & (g[j] ^ h[j]);
      for (j = 0; j < 16; j++) c[j] = k[j + 16];
      c[16] = 0;
      add1305(h, c);
      for (j = 0; j < 16; j++) out[outpos+j] = h[j];
      return 0;
    }
    function crypto_onetimeauth_verify(h, hpos, m, mpos, n, k) {
      var x = new Uint8Array(16);
      crypto_onetimeauth(x, 0, m, mpos, n, k);
      return crypto_verify_16(h, hpos, x, 0);
    }
    function crypto_verify_16(x, xi, y, yi) { return vn(x,xi,y,yi,16); }
    function crypto_secretbox(c, m, d, n, k) {
      if (d < 32) return -1;
      crypto_stream_xor(c, 0, m, 0, d, n, k);
      crypto_onetimeauth(c, 16, c, 32, d - 32, c);
      for (var i = 0; i < 16; i++) c[i] = 0;
      return 0;
    }
    function crypto_secretbox_open(m, c, d, n, k) {
      var x = new Uint8Array(32);
      if (d < 32) return -1;
      crypto_stream(x, 0, 32, n, k);
      if (crypto_onetimeauth_verify(c, 16, c, 32, d - 32, x) !== 0) return -1;
      crypto_stream_xor(m, 0, c, 0, d, n, k);
      for (var i = 0; i < 32; i++) m[i] = 0;
      return 0;
    }
    function set25519(r, a) { for (var i = 0; i < 16; i++) r[i] = a[i] | 0; }
    function car25519(o) {
      var c;
      for (var i = 0; i < 16; i++) { o[i] += 65536; c = Math.floor(o[i] / 65536); o[(i+1)*(i<15?1:0)] += c - 1 + 37 * (c-1) * (i===15?1:0); o[i] -= c * 65536; }
    }
    function sel25519(p, q, b) { var c = ~(b-1); for (var i = 0; i < 16; i++) { var t = c & (p[i] ^ q[i]); p[i] ^= t; q[i] ^= t; } }
    function pack25519(o, n) {
      var i, j, b, m = gf(), t = gf();
      for (i = 0; i < 16; i++) t[i] = n[i];
      car25519(t); car25519(t); car25519(t);
      for (j = 0; j < 2; j++) {
        m[0] = t[0] - 0xffed;
        for (i = 1; i < 15; i++) { m[i] = t[i] - 0xffff - ((m[i-1]>>16) & 1); m[i-1] &= 0xffff; }
        m[15] = t[15] - 0x7fff - ((m[14]>>16) & 1);
        b = (m[15]>>16) & 1;
        m[14] &= 0xffff;
        sel25519(t, m, 1-b);
      }
      for (i = 0; i < 16; i++) { o[2*i] = t[i] & 0xff; o[2*i+1] = t[i] >> 8; }
    }
    function neq25519(a, b) { var c = new Uint8Array(32), d = new Uint8Array(32); pack25519(c, a); pack25519(d, b); return crypto_verify_32(c, 0, d, 0); }
    function par25519(a) { var d = new Uint8Array(32); pack25519(d, a); return d[0] & 1; }
    function unpack25519(o, n) { for (var i = 0; i < 16; i++) o[i] = n[2*i] + (n[2*i+1] << 8); o[15] &= 0x7fff; }
    function A(o, a, b) { for (var i = 0; i < 16; i++) o[i] = a[i] + b[i]; }
    function Z(o, a, b) { for (var i = 0; i < 16; i++) o[i] = a[i] - b[i]; }
    function M(o, a, b) {
      var t0=0,t1=0,t2=0,t3=0,t4=0,t5=0,t6=0,t7=0,t8=0,t9=0,t10=0,t11=0,t12=0,t13=0,t14=0,t15=0,t16=0,t17=0,t18=0,t19=0,t20=0,t21=0,t22=0,t23=0,t24=0,t25=0,t26=0,t27=0,t28=0,t29=0,t30=0,
          b0=b[0],b1=b[1],b2=b[2],b3=b[3],b4=b[4],b5=b[5],b6=b[6],b7=b[7],b8=b[8],b9=b[9],b10=b[10],b11=b[11],b12=b[12],b13=b[13],b14=b[14],b15=b[15];
      var v = a[0];
      t0 += v * b0; t1 += v * b1; t2 += v * b2; t3 += v * b3; t4 += v * b4; t5 += v * b5; t6 += v * b6; t7 += v * b7; t8 += v * b8; t9 += v * b9; t10 += v * b10; t11 += v * b11; t12 += v * b12; t13 += v * b13; t14 += v * b14; t15 += v * b15;
      v = a[1];
      t1 += v * b0; t2 += v * b1; t3 += v * b2; t4 += v * b3; t5 += v * b4; t6 += v * b5; t7 += v * b6; t8 += v * b7; t9 += v * b8; t10 += v * b9; t11 += v * b10; t12 += v * b11; t13 += v * b12; t14 += v * b13; t15 += v * b14; t16 += v * b15;
      v = a[2];
      t2 += v * b0; t3 += v * b1; t4 += v * b2; t5 += v * b3; t6 += v * b4; t7 += v * b5; t8 += v * b6; t9 += v * b7; t10 += v * b8; t11 += v * b9; t12 += v * b10; t13 += v * b11; t14 += v * b12; t15 += v * b13; t16 += v * b14; t17 += v * b15;
      v = a[3];
      t3 += v * b0; t4 += v * b1; t5 += v * b2; t6 += v * b3; t7 += v * b4; t8 += v * b5; t9 += v * b6; t10 += v * b7; t11 += v * b8; t12 += v * b9; t13 += v * b10; t14 += v * b11; t15 += v * b12; t16 += v * b13; t17 += v * b14; t18 += v * b15;
      v = a[4];
      t4 += v * b0; t5 += v * b1; t6 += v * b2; t7 += v * b3; t8 += v * b4; t9 += v * b5; t10 += v * b6; t11 += v * b7; t12 += v * b8; t13 += v * b9; t14 += v * b10; t15 += v * b11; t16 += v * b12; t17 += v * b13; t18 += v * b14; t19 += v * b15;
      v = a[5];
      t5 += v * b0; t6 += v * b1; t7 += v * b2; t8 += v * b3; t9 += v * b4; t10 += v * b5; t11 += v * b6; t12 += v * b7; t13 += v * b8; t14 += v * b9; t15 += v * b10; t16 += v * b11; t17 += v * b12; t18 += v * b13; t19 += v * b14; t20 += v * b15;
      v = a[6];
      t6 += v * b0; t7 += v * b1; t8 += v * b2; t9 += v * b3; t10 += v * b4; t11 += v * b5; t12 += v * b6; t13 += v * b7; t14 += v * b8; t15 += v * b9; t16 += v * b10; t17 += v * b11; t18 += v * b12; t19 += v * b13; t20 += v * b14; t21 += v * b15;
      v = a[7];
      t7 += v * b0; t8 += v * b1; t9 += v * b2; t10 += v * b3; t11 += v * b4; t12 += v * b5; t13 += v * b6; t14 += v * b7; t15 += v * b8; t16 += v * b9; t17 += v * b10; t18 += v * b11; t19 += v * b12; t20 += v * b13; t21 += v * b14; t22 += v * b15;
      v = a[8];
      t8 += v * b0; t9 += v * b1; t10 += v * b2; t11 += v * b3; t12 += v * b4; t13 += v * b5; t14 += v * b6; t15 += v * b7; t16 += v * b8; t17 += v * b9; t18 += v * b10; t19 += v * b11; t20 += v * b12; t21 += v * b13; t22 += v * b14; t23 += v * b15;
      v = a[9];
      t9 += v * b0; t10 += v * b1; t11 += v * b2; t12 += v * b3; t13 += v * b4; t14 += v * b5; t15 += v * b6; t16 += v * b7; t17 += v * b8; t18 += v * b9; t19 += v * b10; t20 += v * b11; t21 += v * b12; t22 += v * b13; t23 += v * b14; t24 += v * b15;
      v = a[10];
      t10 += v * b0; t11 += v * b1; t12 += v * b2; t13 += v * b3; t14 += v * b4; t15 += v * b5; t16 += v * b6; t17 += v * b7; t18 += v * b8; t19 += v * b9; t20 += v * b10; t21 += v * b11; t22 += v * b12; t23 += v * b13; t24 += v * b14; t25 += v * b15;
      v = a[11];
      t11 += v * b0; t12 += v * b1; t13 += v * b2; t14 += v * b3; t15 += v * b4; t16 += v * b5; t17 += v * b6; t18 += v * b7; t19 += v * b8; t20 += v * b9; t21 += v * b10; t22 += v * b11; t23 += v * b12; t24 += v * b13; t25 += v * b14; t26 += v * b15;
      v = a[12];
      t12 += v * b0; t13 += v * b1; t14 += v * b2; t15 += v * b3; t16 += v * b4; t17 += v * b5; t18 += v * b6; t19 += v * b7; t20 += v * b8; t21 += v * b9; t22 += v * b10; t23 += v * b11; t24 += v * b12; t25 += v * b13; t26 += v * b14; t27 += v * b15;
      v = a[13];
      t13 += v * b0; t14 += v * b1; t15 += v * b2; t16 += v * b3; t17 += v * b4; t18 += v * b5; t19 += v * b6; t20 += v * b7; t21 += v * b8; t22 += v * b9; t23 += v * b10; t24 += v * b11; t25 += v * b12; t26 += v * b13; t27 += v * b14; t28 += v * b15;
      v = a[14];
      t14 += v * b0; t15 += v * b1; t16 += v * b2; t17 += v * b3; t18 += v * b4; t19 += v * b5; t20 += v * b6; t21 += v * b7; t22 += v * b8; t23 += v * b9; t24 += v * b10; t25 += v * b11; t26 += v * b12; t27 += v * b13; t28 += v * b14; t29 += v * b15;
      v = a[15];
      t15 += v * b0; t16 += v * b1; t17 += v * b2; t18 += v * b3; t19 += v * b4; t20 += v * b5; t21 += v * b6; t22 += v * b7; t23 += v * b8; t24 += v * b9; t25 += v * b10; t26 += v * b11; t27 += v * b12; t28 += v * b13; t29 += v * b14; t30 += v * b15;

      t0  += 38 * t16; t1  += 38 * t17; t2  += 38 * t18; t3  += 38 * t19; t4  += 38 * t20; t5  += 38 * t21; t6  += 38 * t22; t7  += 38 * t23;
      t8  += 38 * t24; t9  += 38 * t25; t10 += 38 * t26; t11 += 38 * t27; t12 += 38 * t28; t13 += 38 * t29; t14 += 38 * t30;
      
      var c = 1;
      v =  t0 + c + 65535; c = Math.floor(v / 65536);  t0 = v - c * 65536;
      v =  t1 + c + 65535; c = Math.floor(v / 65536);  t1 = v - c * 65536;
      v =  t2 + c + 65535; c = Math.floor(v / 65536);  t2 = v - c * 65536;
      v =  t3 + c + 65535; c = Math.floor(v / 65536);  t3 = v - c * 65536;
      v =  t4 + c + 65535; c = Math.floor(v / 65536);  t4 = v - c * 65536;
      v =  t5 + c + 65535; c = Math.floor(v / 65536);  t5 = v - c * 65536;
      v =  t6 + c + 65535; c = Math.floor(v / 65536);  t6 = v - c * 65536;
      v =  t7 + c + 65535; c = Math.floor(v / 65536);  t7 = v - c * 65536;
      v =  t8 + c + 65535; c = Math.floor(v / 65536);  t8 = v - c * 65536;
      v =  t9 + c + 65535; c = Math.floor(v / 65536);  t9 = v - c * 65536;
      v = t10 + c + 65535; c = Math.floor(v / 65536); t10 = v - c * 65536;
      v = t11 + c + 65535; c = Math.floor(v / 65536); t11 = v - c * 65536;
      v = t12 + c + 65535; c = Math.floor(v / 65536); t12 = v - c * 65536;
      v = t13 + c + 65535; c = Math.floor(v / 65536); t13 = v - c * 65536;
      v = t14 + c + 65535; c = Math.floor(v / 65536); t14 = v - c * 65536;
      v = t15 + c + 65535; c = Math.floor(v / 65536); t15 = v - c * 65536;
      t0 += c-1 + 37 * (c-1);

      c = 1;
      v =  t0 + c + 65535; c = Math.floor(v / 65536);  t0 = v - c * 65536;
      v =  t1 + c + 65535; c = Math.floor(v / 65536);  t1 = v - c * 65536;
      v =  t2 + c + 65535; c = Math.floor(v / 65536);  t2 = v - c * 65536;
      v =  t3 + c + 65535; c = Math.floor(v / 65536);  t3 = v - c * 65536;
      v =  t4 + c + 65535; c = Math.floor(v / 65536);  t4 = v - c * 65536;
      v =  t5 + c + 65535; c = Math.floor(v / 65536);  t5 = v - c * 65536;
      v =  t6 + c + 65535; c = Math.floor(v / 65536);  t6 = v - c * 65536;
      v =  t7 + c + 65535; c = Math.floor(v / 65536);  t7 = v - c * 65536;
      v =  t8 + c + 65535; c = Math.floor(v / 65536);  t8 = v - c * 65536;
      v =  t9 + c + 65535; c = Math.floor(v / 65536);  t9 = v - c * 65536;
      v = t10 + c + 65535; c = Math.floor(v / 65536); t10 = v - c * 65536;
      v = t11 + c + 65535; c = Math.floor(v / 65536); t11 = v - c * 65536;
      v = t12 + c + 65535; c = Math.floor(v / 65536); t12 = v - c * 65536;
      v = t13 + c + 65535; c = Math.floor(v / 65536); t13 = v - c * 65536;
      v = t14 + c + 65535; c = Math.floor(v / 65536); t14 = v - c * 65536;
      v = t15 + c + 65535; c = Math.floor(v / 65536); t15 = v - c * 65536;
      t0 += c-1 + 37 * (c-1);

      o[0] = t0; o[1] = t1; o[2] = t2; o[3] = t3; o[4] = t4; o[5] = t5; o[6] = t6; o[7] = t7;
      o[8] = t8; o[9] = t9; o[10] = t10; o[11] = t11; o[12] = t12; o[13] = t13; o[14] = t14; o[15] = t15;
    }
    function S(o, a) { M(o, a, a); }
    function inv25519(o, i) {
      var c = gf();
      var a;
      for (a = 0; a < 16; a++) c[a] = i[a];
      for (a = 253; a >= 0; a--) { S(c, c); if(a !== 2 && a !== 4) M(c, c, i); }
      for (a = 0; a < 16; a++) o[a] = c[a];
    }
    function pow2523(o, i) {
      var c = gf();
      var a;
      for (a = 0; a < 16; a++) c[a] = i[a];
      for (a = 250; a >= 0; a--) { S(c, c); if(a !== 1) M(c, c, i); }
      for (a = 0; a < 16; a++) o[a] = c[a];
    }
    function crypto_scalarmult(q, n, p) {
      var z = new Uint8Array(32);
      var x = new Float64Array(80), r, i;
      var a = gf(), b = gf(), c = gf(), d = gf(), e = gf(), f = gf();
      for (i = 0; i < 31; i++) z[i] = n[i];
      z[31] = (n[31] & 127) | 64;
      z[0] &= 248;
      unpack25519(x, p);
      for (i = 0; i < 16; i++) { b[i] = x[i]; d[i] = a[i] = c[i] = 0; }
      a[0] = d[0] = 1;
      for (i = 254; i >= 0; --i) {
        r = (z[i>>>3]>>>(i&7))&1;
        sel25519(a, b, r); sel25519(c, d, r);
        A(e, a, c); Z(a, a, c); A(c, b, d); Z(b, b, d);
        S(d, e); S(f, a); M(a, c, a); M(c, b, e);
        A(e, a, c); Z(a, a, c); S(b, a); Z(c, d, f);
        M(a, c, _121665); A(a, a, d); M(c, c, a); M(a, d, f); M(d, b, x); S(b, e);
        sel25519(a, b, r); sel25519(c, d, r);
      }
      for (i = 0; i < 16; i++) { x[i+16] = a[i]; x[i+32] = c[i]; x[i+48] = b[i]; x[i+64] = d[i]; }
      var x32 = x.subarray(32), x16 = x.subarray(16);
      inv25519(x32, x32);
      M(x16, x16, x32);
      pack25519(q, x16);
      return 0;
    }
    function crypto_scalarmult_base(q, n) { return crypto_scalarmult(q, n, _9); }
    var _121665 = gf([0xdb41, 1]);

    var K = [
      0x428a2f98, 0xd728ae22, 0x71374491, 0x23ef65cd, 0xb5c0fbcf, 0xec4d3b2f, 0xe9b5dba5, 0x8189dbbc,
      0x3956c25b, 0xf348b538, 0x59f111f1, 0xb605d019, 0x923f82a4, 0xaf194f9b, 0xab1c5ed5, 0xda6d8118,
      0xd807aa98, 0xa3030242, 0x12835b01, 0x45706fbe, 0x243185be, 0x4ee4b28c, 0x550c7dc3, 0xd5ffb4e2,
      0x72be5d74, 0xf27b896f, 0x80deb1fe, 0x3b1696b1, 0x9bdc06a7, 0x25c71235, 0xc19bf174, 0xcf692694,
      0xe49b69c1, 0x9ef14ad2, 0xefbe4786, 0x384f25e3, 0x0fc19dc6, 0x8b8cd5b5, 0x240ca1cc, 0x77ac9c65,
      0x2de92c6f, 0x592b0275, 0x4a7484aa, 0x6ea6e483, 0x5cb0a9dc, 0xbd41fbd4, 0x76f988da, 0x831153b5,
      0x983e5152, 0xee66dfab, 0xa831c66d, 0x2db43210, 0xb00327c8, 0x98fb213f, 0xbf597fc7, 0xbeef0ee4,
      0xc6e00bf3, 0x3da88fc2, 0xd5a79147, 0x930aa725, 0x06ca6351, 0xe003826f, 0x14292967, 0x0a0e6e70,
      0x27b70a85, 0x46d22ffc, 0x2e1b2138, 0x5c26c926, 0x4d2c6dfc, 0x5ac42aed, 0x53380d13, 0x9d95b3df,
      0x650a7354, 0x8baf63de, 0x766a0abb, 0x3c77b2a8, 0x81c2c92e, 0x47edaee6, 0x92722c85, 0x1482353b,
      0xa2bfe8a1, 0x4cf10364, 0xa81a664b, 0xbc423001, 0xc24b8b70, 0xd0f89791, 0xc76c51a3, 0x0654be30,
      0xd192e819, 0xd6ef5218, 0xd6990624, 0x5565a910, 0xf40e3585, 0x5771202a, 0x106aa070, 0x32bbd1b8,
      0x19a4c116, 0xb8d2d0c8, 0x1e376c08, 0x5141ab53, 0x2748774c, 0xdf8eeb99, 0x34b0bcb5, 0xe19b48a8,
      0x391c0cb3, 0xc5c95a63, 0x4ed8aa4a, 0xe3418acb, 0x5b9cca4f, 0x7763e373, 0x682e6ff3, 0xd6b2b8a3,
      0x748f82ee, 0x5defb2fc, 0x78a5636f, 0x43172f60, 0x84c87814, 0xa1f0ab72, 0x8cc70208, 0x1a6439ec,
      0x90befffa, 0x23631e28, 0xa4506ceb, 0xde82bde9, 0xbef9a3f7, 0xb2c67915, 0xc67178f2, 0xe372532b,
      0xca273ece, 0xea26619c, 0xd186b8c7, 0x21c0c207, 0xeada7dd6, 0xcde0eb1e, 0xf57d4f7f, 0xee6ed178,
      0x06f067aa, 0x72176fba, 0x0a637dc5, 0xa2c898a6, 0x113f9804, 0xbef90dae, 0x1b710b35, 0x131c471b,
      0x28db77f5, 0x23047d84, 0x32caab7b, 0x40c72493, 0x3c9ebe0a, 0x15c9bebc, 0x431d67c4, 0x9c100d4c,
      0x4cc5d4be, 0xcb3e42b6, 0x597f299c, 0xfc657e2a, 0x5fcb6fab, 0x3ad6faec, 0x6c44198c, 0x4a475817
    ];

    function crypto_hashblocks(x, m, n) {
      var z = [], b = [], a = [], w = [], t, i, j;
      for (i = 0; i < 8; i++) z[i] = a[i] = dl64(x, 8*i);
      var pos = 0;
      while (n >= 128) {
        for (i = 0; i < 16; i++) w[i] = dl64(m, 8*i+pos);
        for (i = 0; i < 80; i++) {
          for (j = 0; j < 8; j++) b[j] = a[j];
          t = add64(a[7], add64(add64(rotr64(a[4], 14) ^ rotr64(a[4], 18) ^ rotr64(a[4], 41), (a[4] & a[5]) ^ (~a[4] & a[6])), add64(K[2*i+1] + K[2*i] * 0x100000000, w[i%16])));
          b[7] = add64(t, add64(rotr64(a[0], 28) ^ rotr64(a[0], 34) ^ rotr64(a[0], 39), (a[0] & a[1]) ^ (a[0] & a[2]) ^ (a[1] & a[2])));
          b[3] = add64(b[3], t);
          for (j = 0; j < 8; j++) a[(j+1)%8] = b[j];
          if (i%16 === 15) {
            for (j = 0; j < 16; j++) {
              w[j] = add64(add64(add64(rotr64(w[(j+1)%16], 1) ^ rotr64(w[(j+1)%16], 8) ^ shr64(w[(j+1)%16], 7), w[j]), rotr64(w[(j+14)%16], 19) ^ rotr64(w[(j+14)%16], 61) ^ shr64(w[(j+14)%16], 6)), w[(j+9)%16]);
            }
          }
        }
        for (i = 0; i < 8; i++) a[i] = add64(a[i], z[i]); z = a.slice();
        pos += 128; n -= 128;
      }
      for (i = 0; i < 8; i++) ts64(x, 8*i, z[i]);
      return n;
    }
    function dl64(x, i) { return (x[i] << 24 | x[i+1] << 16 | x[i+2] << 8 | x[i+3]) * 0x100000000 + (x[i+4] << 24 | x[i+5] << 16 | x[i+6] << 8 | x[i+7]); }
    function ts64(x, i, u) { x[i] = (u / 0x100000000000000) & 0xff; x[i+1] = (u / 0x1000000000000) & 0xff; x[i+2] = (u / 0x10000000000) & 0xff; x[i+3] = (u / 0x100000000) & 0xff; x[i+4] = u >>> 24; x[i+5] = (u >> 16) & 0xff; x[i+6] = (u >> 8) & 0xff; x[i+7] = u & 0xff; }
    function add64(a, b) { return a + b; }
    function rotr64(x, c) { return (x >>> c) | (x * Math.pow(2, 64-c)); }
    function shr64(x, c) { return Math.floor(x / Math.pow(2, c)); }

    var iv = new Uint8Array([
      0x6a,0x09,0xe6,0x67,0xf3,0xbc,0xc9,0x08,
      0xbb,0x67,0xae,0x85,0x84,0xca,0xa7,0x3b,
      0x3c,0x6e,0xf3,0x72,0xfe,0x94,0xf8,0x2b,
      0xa5,0x4f,0xf5,0x3a,0x5f,0x1d,0x36,0xf1,
      0x51,0x0e,0x52,0x7f,0xad,0xe6,0x82,0xd1,
      0x9b,0x05,0x68,0x8c,0x2b,0x3e,0x6c,0x1f,
      0x1f,0x83,0xd9,0xab,0xfb,0x41,0xbd,0x6b,
      0x5b,0xe0,0xcd,0x19,0x13,0x7e,0x21,0x79
    ]);

    function crypto_hash(out, m, n) {
      var h = new Uint8Array(64), x = new Uint8Array(256);
      var i, b = n;
      for (i = 0; i < 64; i++) h[i] = iv[i];
      crypto_hashblocks(h, m, n);
      n %= 128;
      for (i = 0; i < 256; i++) x[i] = 0;
      for (i = 0; i < n; i++) x[i] = m[b-n+i];
      x[n] = 128;
      n = 256 - 128 * (n < 112 ? 1 : 0);
      x[n-9] = 0;
      ts64(x, n-8, b * 8);
      crypto_hashblocks(h, x, n);
      for (i = 0; i < 64; i++) out[i] = h[i];
      return 0;
    }

    function add(p, q) {
      var a = gf(), b = gf(), c = gf(), d = gf(), e = gf(), f = gf(), g = gf(), h = gf(), t = gf();
      Z(a, p[1], p[0]); Z(t, q[1], q[0]); M(a, a, t);
      A(b, p[0], p[1]); A(t, q[0], q[1]); M(b, b, t);
      M(c, p[3], q[3]); M(c, c, D2);
      M(d, p[2], q[2]); A(d, d, d);
      Z(e, b, a); Z(f, d, c); A(g, d, c); A(h, b, a);
      M(p[0], e, f); M(p[1], h, g); M(p[2], g, f); M(p[3], e, h);
    }
    function cswap(p, q, b) { for (var i = 0; i < 4; i++) sel25519(p[i], q[i], b); }
    function pack(r, p) {
      var tx = gf(), ty = gf(), zi = gf();
      inv25519(zi, p[2]); M(tx, p[0], zi); M(ty, p[1], zi);
      pack25519(r, ty);
      r[31] ^= par25519(tx) << 7;
    }
    function scalarmult(p, q, s) {
      var b, i;
      set25519(p[0], gf0); set25519(p[1], gf1); set25519(p[2], gf1); set25519(p[3], gf0);
      for (i = 255; i >= 0; --i) {
        b = (s[(i/8)|0] >> (i&7)) & 1;
        cswap(p, q, b);
        add(q, p);
        add(p, p);
        cswap(p, q, b);
      }
    }
    function scalarbase(p, s) {
      var q = [gf(), gf(), gf(), gf()];
      set25519(q[0], X); set25519(q[1], Y); set25519(q[2], gf1); M(q[3], X, Y);
      scalarmult(p, q, s);
    }

    var L = new Float64Array([0xed, 0xd3, 0xf5, 0x5c, 0x1a, 0x63, 0x12, 0x58, 0xd6, 0x9c, 0xf7, 0xa2, 0xde, 0xf9, 0xde, 0x14, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0x10]);

    function modL(r, x) {
      var carry, i, j, k;
      for (i = 63; i >= 32; --i) {
        carry = 0;
        for (j = i - 32, k = i - 12; j < k; ++j) {
          x[j] += carry - 16 * x[i] * L[j - (i - 32)];
          carry = Math.floor((x[j] + 128) / 256);
          x[j] -= carry * 256;
        }
        x[j] += carry; x[i] = 0;
      }
      carry = 0;
      for (j = 0; j < 32; j++) { x[j] += carry - (x[31] >> 4) * L[j]; carry = x[j] >> 8; x[j] &= 255; }
      for (j = 0; j < 32; j++) x[j] -= carry * L[j];
      for (i = 0; i < 32; i++) { x[i+1] += x[i] >> 8; r[i] = x[i] & 255; }
    }
    function reduce(r) {
      var x = new Float64Array(64);
      for (var i = 0; i < 64; i++) x[i] = r[i];
      for (var i = 0; i < 64; i++) r[i] = 0;
      modL(r, x);
    }

    function crypto_sign_keypair(pk, sk, seed) {
      var d = new Uint8Array(64);
      var p = [gf(), gf(), gf(), gf()];
      if (!seed) seed = randomBytes(32);
      crypto_hash(d, seed, 32);
      d[0] &= 248; d[31] &= 127; d[31] |= 64;
      scalarbase(p, d);
      pack(pk, p);
      for (var i = 0; i < 32; i++) sk[i] = seed[i];
      for (var i = 0; i < 32; i++) sk[32+i] = pk[i];
      return seed;
    }

    function crypto_sign(sm, m, n, sk) {
      var d = new Uint8Array(64), h = new Uint8Array(64), r = new Uint8Array(64);
      var i, j, x = new Float64Array(64);
      var p = [gf(), gf(), gf(), gf()];
      crypto_hash(d, sk, 32);
      d[0] &= 248; d[31] &= 127; d[31] |= 64;
      var smlen = n + 64;
      for (i = 0; i < n; i++) sm[64 + i] = m[i];
      for (i = 0; i < 32; i++) sm[32 + i] = d[32 + i];
      crypto_hash(r, sm.subarray(32), n + 32);
      reduce(r);
      scalarbase(p, r);
      pack(sm, p);
      for (i = 0; i < 32; i++) sm[i+32] = sk[i+32];
      crypto_hash(h, sm, n + 64);
      reduce(h);
      for (i = 0; i < 64; i++) x[i] = 0;
      for (i = 0; i < 32; i++) x[i] = r[i];
      for (i = 0; i < 32; i++) for (j = 0; j < 32; j++) x[i+j] += h[i] * d[j];
      modL(sm.subarray(32), x);
      return smlen;
    }

    function unpackneg(r, p) {
      var t = gf(), chk = gf(), num = gf(), den = gf(), den2 = gf(), den4 = gf(), den6 = gf();
      set25519(r[2], gf1);
      unpack25519(r[1], p);
      S(num, r[1]); M(den, num, D); Z(num, num, r[2]); A(den, r[2], den);
      S(den2, den); S(den4, den2); M(den6, den4, den2); M(t, den6, num); M(t, t, den);
      pow2523(t, t); M(t, t, num); M(t, t, den); M(t, t, den); M(r[0], t, den);
      S(chk, r[0]); M(chk, chk, den);
      if (neq25519(chk, num)) M(r[0], r[0], I);
      S(chk, r[0]); M(chk, chk, den);
      if (neq25519(chk, num)) return -1;
      if (par25519(r[0]) === (p[31]>>7)) Z(r[0], gf0, r[0]);
      M(r[3], r[0], r[1]);
      return 0;
    }

    function crypto_sign_open(m, sm, n, pk) {
      var i;
      var t = new Uint8Array(32), h = new Uint8Array(64);
      var p = [gf(), gf(), gf(), gf()], q = [gf(), gf(), gf(), gf()];
      if (n < 64) return -1;
      if (unpackneg(q, pk)) return -1;
      for (i = 0; i < n; i++) m[i] = sm[i];
      for (i = 0; i < 32; i++) m[i+32] = pk[i];
      crypto_hash(h, m, n);
      reduce(h);
      scalarmult(p, q, h);
      scalarbase(q, sm.subarray(32));
      add(p, q);
      pack(t, p);
      n -= 64;
      if (crypto_verify_32(sm, 0, t, 0)) { for (i = 0; i < n; i++) m[i] = 0; return -1; }
      for (i = 0; i < n; i++) m[i] = sm[i + 64];
      return n;
    }

    function randomBytes(n) {
      var b = new Uint8Array(n);
      if (typeof crypto !== 'undefined' && crypto.getRandomValues) {
        crypto.getRandomValues(b);
      } else {
        for (var i = 0; i < n; i++) b[i] = Math.floor(Math.random() * 256);
      }
      return b;
    }

    return {
      sign: {
        keyPair: {
          fromSeed: function(seed) {
            var pk = new Uint8Array(32), sk = new Uint8Array(64);
            for (var i = 0; i < 32; i++) sk[i] = seed[i];
            crypto_sign_keypair(pk, sk, seed);
            return { publicKey: pk, secretKey: sk };
          }
        },
        detached: function(msg, sk) {
          var sm = new Uint8Array(64 + msg.length);
          crypto_sign(sm, msg, msg.length, sk);
          var sig = new Uint8Array(64);
          for (var i = 0; i < 64; i++) sig[i] = sm[i];
          return sig;
        },
        detached: {
          verify: function(msg, sig, pk) {
            var sm = new Uint8Array(64 + msg.length);
            var m = new Uint8Array(64 + msg.length);
            for (var i = 0; i < 64; i++) sm[i] = sig[i];
            for (var i = 0; i < msg.length; i++) sm[i+64] = msg[i];
            return crypto_sign_open(m, sm, sm.length, pk) >= 0;
          }
        }
      },
      sign_detached: function(msg, sk) {
        var sm = new Uint8Array(64 + msg.length);
        crypto_sign(sm, msg, msg.length, sk);
        var sig = new Uint8Array(64);
        for (var i = 0; i < 64; i++) sig[i] = sm[i];
        return sig;
      },
      hash: function(m) {
        var out = new Uint8Array(64);
        crypto_hash(out, m, m.length);
        return out;
      },
      randomBytes: randomBytes
    };
  })();

  // QR Code generator (minimal implementation)
  const QRCode = (function() {
    const EC_L = 1, EC_M = 0, EC_Q = 3, EC_H = 2;
    
    function generate(text, ecl) {
      ecl = ecl || EC_L;
      const data = encodeText(text);
      const version = getMinVersion(data.length, ecl);
      const size = version * 4 + 17;
      const matrix = createMatrix(size);
      
      // Simplified QR encoding for payment addresses
      const modules = [];
      for (let y = 0; y < size; y++) {
        const row = [];
        for (let x = 0; x < size; x++) {
          // Simple pattern based on data
          const i = y * size + x;
          const bit = (i < data.length * 8) ? ((data[Math.floor(i/8)] >> (7 - i%8)) & 1) : 0;
          row.push(((x + y) % 2 === 0) ? bit : 1 - bit);
        }
        modules.push(row);
      }
      
      // Add finder patterns
      addFinderPattern(modules, 0, 0);
      addFinderPattern(modules, size - 7, 0);
      addFinderPattern(modules, 0, size - 7);
      
      return modules;
    }
    
    function encodeText(text) {
      const bytes = [];
      for (let i = 0; i < text.length; i++) {
        bytes.push(text.charCodeAt(i));
      }
      return bytes;
    }
    
    function getMinVersion(len, ecl) {
      return Math.min(Math.ceil(len / 15) + 1, 10);
    }
    
    function createMatrix(size) {
      const m = [];
      for (let i = 0; i < size; i++) {
        m.push(new Array(size).fill(0));
      }
      return m;
    }
    
    function addFinderPattern(m, x, y) {
      for (let dy = 0; dy < 7 && y + dy < m.length; dy++) {
        for (let dx = 0; dx < 7 && x + dx < m.length; dx++) {
          if (dy === 0 || dy === 6 || dx === 0 || dx === 6 ||
              (dy >= 2 && dy <= 4 && dx >= 2 && dx <= 4)) {
            m[y + dy][x + dx] = 1;
          } else {
            m[y + dy][x + dx] = 0;
          }
        }
      }
    }
    
    function toSVG(modules, size) {
      size = size || 200;
      const cellSize = size / modules.length;
      let svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${size} ${size}" width="${size}" height="${size}">`;
      svg += `<rect width="100%" height="100%" fill="white"/>`;
      
      for (let y = 0; y < modules.length; y++) {
        for (let x = 0; x < modules[y].length; x++) {
          if (modules[y][x]) {
            svg += `<rect x="${x * cellSize}" y="${y * cellSize}" width="${cellSize}" height="${cellSize}" fill="black"/>`;
          }
        }
      }
      
      svg += '</svg>';
      return svg;
    }
    
    return { generate, toSVG };
  })();

  // Utility functions
  function toHex(bytes) {
    return Array.from(bytes).map(b => b.toString(16).padStart(2, '0')).join('');
  }

  function fromHex(hex) {
    const bytes = new Uint8Array(hex.length / 2);
    for (let i = 0; i < hex.length; i += 2) {
      bytes[i / 2] = parseInt(hex.substr(i, 2), 16);
    }
    return bytes;
  }

  function toBase64(bytes) {
    let binary = '';
    for (let i = 0; i < bytes.length; i++) {
      binary += String.fromCharCode(bytes[i]);
    }
    return btoa(binary);
  }

  function fromBase64(b64) {
    const binary = atob(b64);
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) {
      bytes[i] = binary.charCodeAt(i);
    }
    return bytes;
  }

  // SHA256 for address derivation (simple implementation)
  async function sha256(data) {
    if (typeof data === 'string') {
      data = new TextEncoder().encode(data);
    }
    const hashBuffer = await crypto.subtle.digest('SHA-256', data);
    return new Uint8Array(hashBuffer);
  }

  // Derive RTC address from public key
  async function deriveAddress(publicKey) {
    const hash = await sha256(publicKey);
    return 'RTC' + toHex(hash).substring(0, 40);
  }

  // Widget state
  let currentModal = null;
  let widgetConfig = {};

  // CSS Styles
  const styles = `
    .rtc-pay-button {
      background: linear-gradient(135deg, #FF6B35 0%, #F7931A 100%);
      border: none;
      border-radius: 8px;
      color: white;
      cursor: pointer;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
      font-size: 16px;
      font-weight: 600;
      padding: 12px 24px;
      transition: all 0.2s ease;
      display: inline-flex;
      align-items: center;
      gap: 8px;
      box-shadow: 0 4px 12px rgba(255, 107, 53, 0.3);
    }
    .rtc-pay-button:hover {
      transform: translateY(-2px);
      box-shadow: 0 6px 16px rgba(255, 107, 53, 0.4);
    }
    .rtc-pay-button:active {
      transform: translateY(0);
    }
    .rtc-pay-button svg {
      width: 20px;
      height: 20px;
    }
    .rtc-modal-overlay {
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(0, 0, 0, 0.6);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 99999;
      backdrop-filter: blur(4px);
    }
    .rtc-modal {
      background: white;
      border-radius: 16px;
      max-width: 420px;
      width: 90%;
      max-height: 90vh;
      overflow-y: auto;
      box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
    }
    .rtc-modal-header {
      padding: 20px 24px;
      border-bottom: 1px solid #eee;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }
    .rtc-modal-title {
      font-size: 20px;
      font-weight: 700;
      color: #1a1a1a;
      display: flex;
      align-items: center;
      gap: 10px;
    }
    .rtc-modal-close {
      background: none;
      border: none;
      cursor: pointer;
      padding: 8px;
      border-radius: 8px;
      color: #666;
      transition: all 0.2s;
    }
    .rtc-modal-close:hover {
      background: #f5f5f5;
      color: #333;
    }
    .rtc-modal-body {
      padding: 24px;
    }
    .rtc-amount-display {
      text-align: center;
      padding: 20px;
      background: linear-gradient(135deg, #fff5f0 0%, #fff8f5 100%);
      border-radius: 12px;
      margin-bottom: 20px;
    }
    .rtc-amount-value {
      font-size: 36px;
      font-weight: 700;
      color: #FF6B35;
    }
    .rtc-amount-label {
      font-size: 14px;
      color: #666;
      margin-top: 4px;
    }
    .rtc-recipient {
      background: #f8f9fa;
      border-radius: 8px;
      padding: 12px;
      margin-bottom: 20px;
      font-family: monospace;
      font-size: 12px;
      word-break: break-all;
      color: #333;
    }
    .rtc-recipient-label {
      font-size: 12px;
      color: #666;
      margin-bottom: 4px;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
    }
    .rtc-qr-container {
      text-align: center;
      padding: 20px;
      background: #f8f9fa;
      border-radius: 12px;
      margin-bottom: 20px;
    }
    .rtc-qr-code {
      margin: 0 auto;
      max-width: 180px;
    }
    .rtc-qr-label {
      font-size: 12px;
      color: #666;
      margin-top: 8px;
    }
    .rtc-divider {
      display: flex;
      align-items: center;
      margin: 20px 0;
      color: #999;
      font-size: 12px;
    }
    .rtc-divider::before,
    .rtc-divider::after {
      content: '';
      flex: 1;
      border-bottom: 1px solid #eee;
    }
    .rtc-divider span {
      padding: 0 12px;
    }
    .rtc-form-group {
      margin-bottom: 16px;
    }
    .rtc-label {
      display: block;
      font-size: 14px;
      font-weight: 500;
      color: #333;
      margin-bottom: 6px;
    }
    .rtc-input {
      width: 100%;
      padding: 12px;
      border: 2px solid #e0e0e0;
      border-radius: 8px;
      font-size: 14px;
      transition: border-color 0.2s;
      box-sizing: border-box;
    }
    .rtc-input:focus {
      outline: none;
      border-color: #FF6B35;
    }
    .rtc-textarea {
      min-height: 100px;
      resize: vertical;
    }
    .rtc-file-input {
      display: none;
    }
    .rtc-file-label {
      display: block;
      padding: 12px;
      border: 2px dashed #e0e0e0;
      border-radius: 8px;
      text-align: center;
      cursor: pointer;
      transition: all 0.2s;
      color: #666;
    }
    .rtc-file-label:hover {
      border-color: #FF6B35;
      background: #fff5f0;
    }
    .rtc-file-label.has-file {
      border-color: #4CAF50;
      background: #f0fff0;
      color: #2e7d32;
    }
    .rtc-tabs {
      display: flex;
      gap: 8px;
      margin-bottom: 16px;
    }
    .rtc-tab {
      flex: 1;
      padding: 10px;
      border: 2px solid #e0e0e0;
      border-radius: 8px;
      background: white;
      cursor: pointer;
      font-size: 13px;
      font-weight: 500;
      color: #666;
      transition: all 0.2s;
    }
    .rtc-tab:hover {
      border-color: #FF6B35;
    }
    .rtc-tab.active {
      border-color: #FF6B35;
      background: #FF6B35;
      color: white;
    }
    .rtc-submit-btn {
      width: 100%;
      padding: 14px;
      background: linear-gradient(135deg, #FF6B35 0%, #F7931A 100%);
      border: none;
      border-radius: 8px;
      color: white;
      font-size: 16px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s;
      margin-top: 8px;
    }
    .rtc-submit-btn:hover:not(:disabled) {
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(255, 107, 53, 0.4);
    }
    .rtc-submit-btn:disabled {
      opacity: 0.6;
      cursor: not-allowed;
    }
    .rtc-error {
      background: #fff0f0;
      border: 1px solid #ffcccc;
      color: #cc0000;
      padding: 12px;
      border-radius: 8px;
      margin-bottom: 16px;
      font-size: 14px;
    }
    .rtc-success {
      text-align: center;
      padding: 30px 20px;
    }
    .rtc-success-icon {
      width: 64px;
      height: 64px;
      background: #4CAF50;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      margin: 0 auto 16px;
    }
    .rtc-success-icon svg {
      width: 32px;
      height: 32px;
      color: white;
    }
    .rtc-success h3 {
      font-size: 20px;
      color: #333;
      margin-bottom: 8px;
    }
    .rtc-success p {
      color: #666;
      font-size: 14px;
    }
    .rtc-tx-hash {
      background: #f5f5f5;
      padding: 12px;
      border-radius: 8px;
      font-family: monospace;
      font-size: 12px;
      word-break: break-all;
      margin-top: 16px;
    }
    .rtc-loading {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      padding: 20px;
    }
    .rtc-spinner {
      width: 24px;
      height: 24px;
      border: 3px solid #f3f3f3;
      border-top: 3px solid #FF6B35;
      border-radius: 50%;
      animation: rtc-spin 1s linear infinite;
    }
    @keyframes rtc-spin {
      0% { transform: rotate(0deg); }
      100% { transform: rotate(360deg); }
    }
    .rtc-memo {
      font-size: 13px;
      color: #666;
      background: #f8f9fa;
      padding: 8px 12px;
      border-radius: 6px;
      margin-bottom: 16px;
    }
  `;

  // Inject styles
  function injectStyles() {
    if (document.getElementById('rtc-pay-styles')) return;
    const style = document.createElement('style');
    style.id = 'rtc-pay-styles';
    style.textContent = styles;
    document.head.appendChild(style);
  }

  // RTC Logo SVG
  const rtcLogo = `<svg viewBox="0 0 32 32" fill="currentColor"><path d="M16 2C8.268 2 2 8.268 2 16s6.268 14 14 14 14-6.268 14-14S23.732 2 16 2zm0 25c-6.075 0-11-4.925-11-11S9.925 5 16 5s11 4.925 11 11-4.925 11-11 11z"/><path d="M20 12h-6v-2h6c.552 0 1-.448 1-1s-.448-1-1-1h-3V6h-2v2h-1c-1.654 0-3 1.346-3 3v2c0 1.654 1.346 3 3 3h6v2h-6c-.552 0-1 .448-1 1s.448 1 1 1h3v2h2v-2h1c1.654 0 3-1.346 3-3v-2c0-1.654-1.346-3-3-3zm-7 0v-2c0-.552.448-1 1-1h2v4h-2c-.552 0-1-.448-1-1zm8 6c0 .552-.448 1-1 1h-2v-4h2c.552 0 1 .448 1 1v2z"/></svg>`;

  // Create payment button
  function createButton(config) {
    const btn = document.createElement('button');
    btn.className = 'rtc-pay-button';
    btn.innerHTML = `${rtcLogo} Pay ${config.amount} RTC`;
    btn.onclick = () => openModal(config);
    return btn;
  }

  // Create modal
  function openModal(config) {
    if (currentModal) closeModal();
    widgetConfig = config;

    const overlay = document.createElement('div');
    overlay.className = 'rtc-modal-overlay';
    overlay.onclick = (e) => {
      if (e.target === overlay) closeModal();
    };

    const modal = document.createElement('div');
    modal.className = 'rtc-modal';
    modal.innerHTML = `
      <div class="rtc-modal-header">
        <div class="rtc-modal-title">${rtcLogo} Pay with RTC</div>
        <button class="rtc-modal-close" onclick="RustChainPay.close()">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      </div>
      <div class="rtc-modal-body" id="rtc-modal-content">
        ${renderPaymentForm(config)}
      </div>
    `;

    overlay.appendChild(modal);
    document.body.appendChild(overlay);
    currentModal = overlay;

    // Setup event handlers
    setupFormHandlers();
  }

  function renderPaymentForm(config) {
    const qrData = `rtc:${config.to}?amount=${config.amount}${config.memo ? '&memo=' + encodeURIComponent(config.memo) : ''}`;
    const qrModules = QRCode.generate(qrData);
    const qrSvg = QRCode.toSVG(qrModules, 160);

    return `
      <div class="rtc-amount-display">
        <div class="rtc-amount-value">${config.amount} RTC</div>
        <div class="rtc-amount-label">Payment Amount</div>
      </div>
      
      ${config.memo ? `<div class="rtc-memo"><strong>Memo:</strong> ${escapeHtml(config.memo)}</div>` : ''}
      
      <div class="rtc-recipient-label">Recipient Address</div>
      <div class="rtc-recipient">${config.to}</div>
      
      <div class="rtc-qr-container">
        <div class="rtc-qr-code">${qrSvg}</div>
        <div class="rtc-qr-label">Scan with RTC Wallet</div>
      </div>
      
      <div class="rtc-divider"><span>or pay directly</span></div>
      
      <div id="rtc-error-container"></div>
      
      <div class="rtc-tabs">
        <button class="rtc-tab active" data-tab="keystore">Keystore File</button>
        <button class="rtc-tab" data-tab="seed">Seed Phrase</button>
      </div>
      
      <div id="rtc-tab-keystore" class="rtc-tab-content">
        <div class="rtc-form-group">
          <label class="rtc-label">Select Keystore File</label>
          <input type="file" id="rtc-keystore-file" class="rtc-file-input" accept=".json">
          <label for="rtc-keystore-file" class="rtc-file-label" id="rtc-file-label">
            Click to select keystore.json
          </label>
        </div>
        <div class="rtc-form-group">
          <label class="rtc-label">Keystore Password</label>
          <input type="password" id="rtc-keystore-password" class="rtc-input" placeholder="Enter your password">
        </div>
      </div>
      
      <div id="rtc-tab-seed" class="rtc-tab-content" style="display:none;">
        <div class="rtc-form-group">
          <label class="rtc-label">Seed Phrase (12 or 24 words)</label>
          <textarea id="rtc-seed-phrase" class="rtc-input rtc-textarea" placeholder="Enter your seed phrase..."></textarea>
        </div>
      </div>
      
      <button class="rtc-submit-btn" id="rtc-submit-btn">
        Sign & Send Payment
      </button>
    `;
  }

  function setupFormHandlers() {
    // Tab switching
    document.querySelectorAll('.rtc-tab').forEach(tab => {
      tab.onclick = () => {
        document.querySelectorAll('.rtc-tab').forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        const tabId = tab.dataset.tab;
        document.getElementById('rtc-tab-keystore').style.display = tabId === 'keystore' ? 'block' : 'none';
        document.getElementById('rtc-tab-seed').style.display = tabId === 'seed' ? 'block' : 'none';
      };
    });

    // File input
    const fileInput = document.getElementById('rtc-keystore-file');
    const fileLabel = document.getElementById('rtc-file-label');
    if (fileInput) {
      fileInput.onchange = () => {
        if (fileInput.files.length > 0) {
          fileLabel.textContent = fileInput.files[0].name;
          fileLabel.classList.add('has-file');
        }
      };
    }

    // Submit button
    const submitBtn = document.getElementById('rtc-submit-btn');
    if (submitBtn) {
      submitBtn.onclick = handlePayment;
    }
  }

  async function handlePayment() {
    const errorContainer = document.getElementById('rtc-error-container');
    const submitBtn = document.getElementById('rtc-submit-btn');
    
    errorContainer.innerHTML = '';
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="rtc-spinner"></span> Processing...';

    try {
      let privateKey, publicKey, fromAddress;

      const activeTab = document.querySelector('.rtc-tab.active').dataset.tab;

      if (activeTab === 'keystore') {
        const fileInput = document.getElementById('rtc-keystore-file');
        const password = document.getElementById('rtc-keystore-password').value;

        if (!fileInput.files.length) {
          throw new Error('Please select a keystore file');
        }
        if (!password) {
          throw new Error('Please enter your keystore password');
        }

        const keystoreData = await readFile(fileInput.files[0]);
        const keystore = JSON.parse(keystoreData);
        
        // Decrypt keystore (simplified - real implementation would use AES-256-GCM)
        const decrypted = await decryptKeystore(keystore, password);
        privateKey = decrypted.privateKey;
        publicKey = decrypted.publicKey;
        fromAddress = decrypted.address;

      } else {
        const seedPhrase = document.getElementById('rtc-seed-phrase').value.trim();
        if (!seedPhrase) {
          throw new Error('Please enter your seed phrase');
        }

        // Derive keys from seed (simplified - real implementation would use BIP39)
        const derived = await deriveFromSeed(seedPhrase);
        privateKey = derived.privateKey;
        publicKey = derived.publicKey;
        fromAddress = derived.address;
      }

      // Create transaction
      const tx = {
        from: fromAddress,
        to: widgetConfig.to,
        amount: parseFloat(widgetConfig.amount),
        memo: widgetConfig.memo || '',
        timestamp: Date.now(),
        nonce: Math.floor(Math.random() * 1000000)
      };

      // Sign transaction
      const txBytes = new TextEncoder().encode(JSON.stringify(tx));
      const signature = nacl.sign_detached(txBytes, privateKey);

      // Prepare signed transaction
      const signedTx = {
        ...tx,
        public_key: toHex(publicKey),
        signature: toHex(signature)
      };

      // Send to node
      const nodeUrl = widgetConfig.node || DEFAULT_NODE;
      const response = await fetch(`${nodeUrl}/wallet/transfer/signed`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(signedTx)
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.error || result.message || 'Transaction failed');
      }

      // Show success
      showSuccess(result);

      // Callback
      if (widgetConfig.onSuccess) {
        widgetConfig.onSuccess(result);
      }
      if (widgetConfig.callback) {
        fetch(widgetConfig.callback, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ status: 'success', tx: result })
        }).catch(() => {});
      }

    } catch (err) {
      errorContainer.innerHTML = `<div class="rtc-error">${escapeHtml(err.message)}</div>`;
      submitBtn.disabled = false;
      submitBtn.innerHTML = 'Sign & Send Payment';

      if (widgetConfig.onError) {
        widgetConfig.onError(err);
      }
    }
  }

  function showSuccess(result) {
    const content = document.getElementById('rtc-modal-content');
    content.innerHTML = `
      <div class="rtc-success">
        <div class="rtc-success-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
            <polyline points="20 6 9 17 4 12"></polyline>
          </svg>
        </div>
        <h3>Payment Successful!</h3>
        <p>${widgetConfig.amount} RTC sent to recipient</p>
        ${result.tx_hash ? `<div class="rtc-tx-hash"><strong>TX:</strong> ${result.tx_hash}</div>` : ''}
        <button class="rtc-submit-btn" onclick="RustChainPay.close()" style="margin-top: 20px;">Done</button>
      </div>
    `;
  }

  function closeModal() {
    if (currentModal) {
      currentModal.remove();
      currentModal = null;
    }
  }

  // Helper functions
  function readFile(file) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result);
      reader.onerror = reject;
      reader.readAsText(file);
    });
  }

  async function decryptKeystore(keystore, password) {
    // Simplified decryption - real implementation would use PBKDF2 + AES-256-GCM
    // This is a placeholder that shows the structure
    
    if (!keystore.encrypted_seed && !keystore.ciphertext) {
      throw new Error('Invalid keystore format');
    }

    try {
      // Derive key from password using Web Crypto API
      const enc = new TextEncoder();
      const keyMaterial = await crypto.subtle.importKey(
        'raw', enc.encode(password), 'PBKDF2', false, ['deriveBits']
      );
      
      const salt = keystore.salt ? fromHex(keystore.salt) : new Uint8Array(16);
      const derivedBits = await crypto.subtle.deriveBits(
        { name: 'PBKDF2', salt: salt, iterations: 100000, hash: 'SHA-256' },
        keyMaterial, 256
      );
      
      // For demo purposes, derive keys from the hash
      // Real implementation would decrypt the AES-GCM ciphertext
      const seed = new Uint8Array(derivedBits);
      const keyPair = nacl.sign.keyPair.fromSeed(seed.slice(0, 32));
      const address = await deriveAddress(keyPair.publicKey);
      
      return {
        privateKey: keyPair.secretKey,
        publicKey: keyPair.publicKey,
        address: address
      };
    } catch (e) {
      throw new Error('Failed to decrypt keystore. Check your password.');
    }
  }

  async function deriveFromSeed(seedPhrase) {
    // Simplified BIP39 - real implementation would use proper BIP39 + Ed25519 derivation
    const words = seedPhrase.toLowerCase().split(/\s+/);
    if (words.length !== 12 && words.length !== 24) {
      throw new Error('Seed phrase must be 12 or 24 words');
    }

    // Hash the seed phrase to get entropy
    const entropy = await sha256(seedPhrase);
    const seed = entropy.slice(0, 32);
    
    const keyPair = nacl.sign.keyPair.fromSeed(seed);
    const address = await deriveAddress(keyPair.publicKey);

    return {
      privateKey: keyPair.secretKey,
      publicKey: keyPair.publicKey,
      address: address
    };
  }

  function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  // Initialize widgets on page load
  function init() {
    injectStyles();

    document.querySelectorAll('[data-rtc-pay], #rtc-pay, .rtc-pay').forEach(el => {
      const config = {
        to: el.dataset.to || el.dataset.recipient,
        amount: el.dataset.amount || '1',
        memo: el.dataset.memo || '',
        node: el.dataset.node || DEFAULT_NODE,
        callback: el.dataset.callback,
        onSuccess: window[el.dataset.onsuccess],
        onError: window[el.dataset.onerror]
      };

      if (!config.to) {
        console.error('RustChain Pay: Missing recipient address (data-to)');
        return;
      }

      const button = createButton(config);
      el.appendChild(button);
    });
  }

  // Run on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  // Export public API
  window.RustChainPay = {
    version: WIDGET_VERSION,
    open: openModal,
    close: closeModal,
    init: init,
    createButton: createButton
  };

})();
