async function gen() {
    const started = Date.now();
    const wait = () => new Promise(r => setTimeout(r, 50));

    while (!(window._TDBotD && typeof window._TDBotD.sign === 'function') && Date.now() - started < 15000)
        await wait();

    // fm.js hands the blackbox to _fmOpt.success; getinfo() is only the fallback when the callback never fires
    while (!window.__td_blackbox && Date.now() - started < 8000)
        await wait();

    let blackbox = window.__td_blackbox || '';

    if (!blackbox) {
        try {
            if (window._fmOpt && typeof window._fmOpt.getinfo === 'function')
                blackbox = window._fmOpt.getinfo() || '';
        } catch (e) { }
    }

    let sign = '';

    try {
        const r = window._TDBotD.sign({ path: "%path%" });
        sign = (r && r.code === 0 && r.sign) ? r.sign : '';
    } catch (e) { }

    localStorage.clear();
    sessionStorage.clear();

    window.name = '';

    return {
        sign: sign,
        blackbox: blackbox
    };
}

gen();