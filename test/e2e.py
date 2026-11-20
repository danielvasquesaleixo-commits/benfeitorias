"""Teste ponta a ponta (Playwright/Chromium, viewport de celular).
Uso: python3 scripts/build.py && python3 test/e2e.py
Gera saídas em test/out/ (xlsx, kml, kmz, json, relatorio.html/.pdf, prints)."""
import asyncio, os, zipfile
from playwright.async_api import async_playwright
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
O = os.path.join(R, 'test/out'); os.makedirs(O, exist_ok=True)
KML = os.path.join(R, 'test/fixtures/teste.kmz')
def fmt_br(v): return f'{v:,.2f}'.replace(',','X').replace('.',',').replace('X','.')
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
    # perímetro com nome só numérico ("20.00"): reconhecido como perímetro e fora do total
    await pg.click('#bVoltar'); await pg.wait_for_timeout(300)
    await pg.set_input_files('#fKml', os.path.join(R, 'test/fixtures/teste_perimetro_numerico.kml')); await pg.wait_for_timeout(500)
    await pg.click('#mOk'); await pg.wait_for_timeout(300)
    tot = await pg.locator('.card:has-text("Total das benfeitorias"):visible').inner_text(); print('total perímetro numérico:', ' '.join(tot.split()))
    assert '3 itens' in tot and '470,00 m²' in tot, tot  # 240 + 150 + 80
    assert 'Perímetro do imóvel' in await pg.locator('.item:has-text("20.00")').inner_text()
    # planta pela trena: imóvel com recortes (todos os cantos em 90°), benfeitoria nova levantada em campo
    lados = [('N',10),('E',3),('N',2),('E',9),('S',3),('O',1.5),('S',1.5),('O',3),('S',2.5),('O',2.5),('S',0.8),('E',0.5),('S',4.2)]  # o último (← 5,5) vem do "Fechar"
    x = y = 0; pts = [(0,0)]
    for d, m in lados + [('O',5.5)]:
      x += {'E':m,'O':-m}.get(d,0); y += {'N':m,'S':-m}.get(d,0); pts.append((x,y))
    esperado = abs(sum(pts[i][0]*pts[i+1][1]-pts[i+1][0]*pts[i][1] for i in range(len(pts)-1)))/2
    await pg.click('#bNovo'); await pg.wait_for_timeout(300); await pg.click('#bPlanta'); await pg.wait_for_timeout(200)
    for d, m in lados:
      await pg.click(f'[data-add={d}]'); await pg.locator('[data-m]').last.fill(str(m).replace('.',','))
    await pg.click('#plFecha'); await pg.wait_for_timeout(100)
    info = await pg.inner_text('#plInfo'); print('planta:', info)
    assert 'fechada' in info
    await pg.select_option('#plPos', 'mapa'); await pg.fill('#plRot', '15')
    await pg.screenshot(path=os.path.join(O,'planta.png'))
    await pg.click('#plOk'); await pg.wait_for_timeout(400)
    r = await pg.evaluate("({g:ITEM.g,kml:ITEM.kml.area,campo:ITEM.campo.area,lados:ITEM.campo.planta.lados.length})"); print('item com planta:', r, 'esperado:', esperado)
    assert r['g'] == 'Polygon' and abs(r['campo']-esperado) < 0.01 and abs(r['kml']-esperado) < 0.05 and r['lados'] == 14, r
    await pg.click('#sFecha'); await pg.wait_for_timeout(200)
    tot = await pg.locator('.card:has-text("Total das benfeitorias"):visible').inner_text()
    assert '4 itens' in tot and fmt_br(470+esperado) in tot, tot
    await pg.click('nav button[data-v=vExp]'); await pg.wait_for_timeout(200)
    async with pg.expect_popup() as pp: await pg.click('[data-x=pdf]')
    rp = await pp.value; await rp.wait_for_timeout(800); html = await rp.content()
    assert 'Croqui (medidas de campo' in html
    await rp.screenshot(path=os.path.join(O,'relatorio_planta.png'), full_page=True)
    # planta não concluída: "Voltar" guarda o rascunho sem mexer na área; foto pela câmera anexa direto
    await rp.close(); await pg.click('nav button[data-v=vLista]'); await pg.wait_for_timeout(200)
    await pg.click('#bNovo'); await pg.wait_for_timeout(300); await pg.click('#bPlanta'); await pg.wait_for_timeout(200)
    for d, m in [('N',6),('E',4)]:
      await pg.click(f'[data-add={d}]'); await pg.locator('[data-m]').last.fill(str(m))
    await pg.click('#plC'); await pg.wait_for_timeout(300)
    bt = await pg.inner_text('#bPlanta'); print('botão após Voltar:', bt)
    assert 'em andamento (2 lados' in bt and await pg.evaluate('ITEM.campo.area') is None
    await pg.click('#bPlanta'); await pg.wait_for_timeout(200)
    assert await pg.locator('[data-m]').count() == 2
    await pg.click('#plC'); await pg.wait_for_timeout(300)
    from PIL import Image; img = os.path.join(O, 'camera.jpg'); Image.new('RGB', (64, 48), (180, 120, 60)).save(img)
    await pg.set_input_files('#fCam', img); await pg.wait_for_timeout(800)
    nf = await pg.evaluate('ITEM.fotos.length'); print('fotos após câmera:', nf); assert nf == 1
    assert await pg.locator('label[for=fCam]').count() == 1
    print('erros JS:', errs); assert not errs
    await b.close()
asyncio.run(main())
