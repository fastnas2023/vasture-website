"""Create colour illustrations from the reviewed HD master; retain source provenance."""
import json
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw

root = Path(__file__).resolve().parents[1]
data_path = root / 'data/catalogue-a4-remaining.json'
data = json.loads(data_path.read_text())
products = data['products'] if isinstance(data, dict) else data
p = next(p for p in products if p['id'] == 'hvj259-reflective-border-tabard')
base = np.array(Image.open(root / 'assets/catalogue-a4/main/hvj259-hi-vis-yellow-ai-v2.webp').convert('RGB'), dtype=float)
mask = np.clip((np.minimum(base[:,:,0],base[:,:,1])-base[:,:,2]-15)/35,0,1)
lum = base @ np.array([.2126,.7152,.0722])
mid = np.median(lum[mask>.99])
out = root / 'assets/catalogue-a4/hvj259-colours-v3'
out.mkdir(parents=True,exist_ok=True)
manifest=[]
sheet=Image.new('RGB',(1000,1200),'white')
draw=ImageDraw.Draw(sheet)
for i,v in enumerate(p['color_variants']):
    previous_review=p.get('colour_image_review',{}).get('variants',[])
    old = previous_review[i]['previous'] if previous_review else v['image']
    original=np.array(Image.open(root/old).convert('RGB'),dtype=float)
    h,w=original.shape[:2]
    color=np.median(original[int(h*.47):int(h*.53),int(w*.47):int(w*.53)].reshape(-1,3),axis=0)
    if i==0:
        result=base
    else:
        shade=(lum-mid)/mid
        recolor=np.clip(color[None,None,:]*(1+shade[:,:,None]*1.4),0,255)
        result=base*(1-mask[:,:,None])+recolor*mask[:,:,None]
    name=Path(old).stem.replace('-ai-v2','')+'-hd-v3.webp'
    path=out/name
    image=Image.fromarray(np.uint8(result))
    image.save(path,'WEBP',quality=94,method=6)
    relative=str(path.relative_to(root))
    manifest.append({'label_zh':v['label_zh'],'label_en':v['label_en'],'source':relative,'previous':old,'method':'HD-master-colour-illustration','sample_rgb':color.tolist()})
    v['image']=relative
    thumb=image.copy();thumb.thumbnail((240,340))
    x=(i%4)*250;y=(i//4)*300
    sheet.paste(thumb,(x,y));draw.text((x+5,y+265),v['label_en'],fill='black')
p['main_image']=manifest[0]['source']
p['gallery_images']=[v['source'] for v in manifest]
p['colour_image_review']={'date':'2026-09-12','method':'HD master with catalogue colour references','variants':manifest}
data_path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
(out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
sheet.save(root/'output/hvj259-review/colours-v3.jpg')
print('Prepared',len(manifest),'HD colour illustrations')
