"""Teste ponta a ponta (Playwright/Chromium, viewport de celular).
Uso: python3 scripts/build.py && python3 test/e2e.py
Gera saídas em test/out/ (xlsx, kml, kmz, json, relatorio.html/.pdf, prints)."""
import asyncio, os, zipfile
from playwright.async_api import async_playwright
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
O = os.path.join(R, 'test/out'); os.makedirs(O, exist_ok=True)
KML = os.path.join(R, 'test/fixtures/teste.kmz')
async def main():
  async with async_playwright() as p:
    b = await p.chromium.launch()
    ctx = await b.new_context(viewport={'width':400,'height':820}, accept_downloads=True, device_scale_factor=2)
    pg = await ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    await pg.goto('file://' + os.path.join(R, 'dist/index.html')); await pg.wait_for_timeout(400)
    await pg.set_input_files('#fKml', KML); await pg.wait_for_timeout(500)
    await pg.fill('#mProc', '0000000-00.0000.8.12.0000'); await pg.click('#mOk'); await pg.wait_for_timeout(300)
    n = await pg.locator('.item').count(); print('itens na lista:', n)
    # casa: acabamentos + descrição
    await pg.click('.item:has-text("Casa sede")'); await pg.wait_for_timeout(200)
    for k, v in [('estr','Alvenaria de tijolos'),('jan','metálicas'),('port','metálicas'),('piso','cerâmico'),('cob','telhas cerâmicas'),('forro','laje')]:
      await pg.fill(f'[data-ac={k}]', v)
    await pg.fill('#iPad','8 - Médio'); await pg.fill('#iCons','E - Regular'); await pg.fill('#iIdade','20')
    await pg.click('#gDesc'); desc = await pg.input_value('#iDesc'); print('descrição casa:', desc)
    assert desc.startswith('Construído em alvenaria de tijolos')
    await pg.click('#sFecha'); await pg.wait_for_timeout(200)
    # curral
    await pg.click('.item:has-text("Curral") >> nth=0'); await pg.wait_for_timeout(200)
    assert await pg.eval_on_selector('#cForm','e=>e.value') == 'circular'
    for sel, v in [('#cLances','110'),('#cEspPal','2,5'),('#cReg','5'),('#cMad','Aroeira'),('#cTronco','1'),('#cBal','1'),('#cDivs','7')]:
      await pg.fill(sel, v)
    await pg.click('#gDesc'); await pg.click('#gDivi')
    print('curral:', await pg.input_value('#iDesc')); print('divisão:', await pg.input_value('#iDivi'))
    await pg.click('#sFecha'); await pg.wait_for_timeout(200)
    await pg.screenshot(path=os.path.join(O,'lista.png'), full_page=True)
    await pg.click('nav button[data-v=vMapa]'); await pg.wait_for_timeout(700); await pg.screenshot(path=os.path.join(O,'mapa.png'))
    await pg.click('nav button[data-v=vExp]'); await pg.wait_for_timeout(200)
    for t, ext in [('xlsx','xlsx'),('kmz','kmz'),('kml','kml'),('bak','json')]:
      async with pg.expect_download() as d: await pg.click(f'[data-x={t}]')
      await (await d.value).save_as(os.path.join(O, 'saida.' + ext))
    async with pg.expect_popup() as pp: await pg.click('[data-x=pdf]')
    rp = await pp.value; await rp.wait_for_timeout(1000)
    open(os.path.join(O,'relatorio.html'),'w',encoding='utf-8').write(await rp.content())
    await rp.emulate_media(media='print'); await rp.pdf(path=os.path.join(O,'relatorio.pdf'), format='A4', print_background=True)
    print('erros JS:', errs); assert not errs
    await b.close()
asyncio.run(main())
