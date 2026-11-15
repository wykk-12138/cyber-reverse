
﻿async function gen() {
    while (!window._fmOpt || !window._fmOpt.sign) {
        await new Promise(r => setTimeout(r, 50));
    }

    let sign = window._fmOpt.sign(
        {
            path: "%path%",
            body: "%body%"
        }
    );

    let blackbox = window._fmOpt.getinfo();

    const result = {
        sign: sign["sign"],
        blackbox: blackbox
    };

    localStorage.clear();
    sessionStorage.clear();

    window.name = '';

    return result;
}