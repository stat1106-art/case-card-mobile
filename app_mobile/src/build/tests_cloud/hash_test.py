import subprocess, sys, time, json
from playwright.sync_api import sync_playwright
srv = subprocess.Popen([sys.executable, "-m", "http.server", "8830", "--bind", "127.0.0.1", "-d", sys.argv[1]], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(1)
try:
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page()
        pg.add_init_script("localStorage.setItem('pastedCases', JSON.stringify([{id:'local_x', data:{format:'case-card-app-case', title:'本機案例', source:{}, card:{}}}]))")
        pg.goto("http://127.0.0.1:8830/repo/#case=shilin_110_laosu_72.json"); pg.wait_for_selector("input[name=c]")
        a = pg.eval_on_selector("input[name=c]:checked", "e=>e.value"); print(("PASS " if a == "shilin_110_laosu_72.json" else "FAIL ") + "#case= 預選網站案例：" + a)
        pg.check("input[value='local_x']"); pg.evaluate("location.hash='#case=../../etc/passwd'"); time.sleep(1)
        c = pg.eval_on_selector("input[name=c]:checked", "e=>e.value"); print(("PASS " if c == "local_x" else "FAIL ") + "#case= 指到不存在的檔名：不跳選、不組路徑（維持 " + c + "）")
        pg.evaluate("location.hash='#case=local_x'"); time.sleep(1)
        print("PASS #case= 不能選僅本機案例（只認網站案例）" if pg.eval_on_selector("input[name=c]:checked", "e=>e.value") == "local_x" else "?")
        b.close()
finally: srv.terminate()
