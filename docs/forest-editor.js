/* Original Forest textures, reconstructed isometric scene, editable browser layout. */
(() => {
  'use strict';
  const C=ForestCore,$=id=>document.getElementById(id),clone=value=>JSON.parse(JSON.stringify(value));
  const canvas=$('forest-canvas'),ctx=canvas.getContext('2d'),shell=$('canvas-shell');
  const STORE='forest-studio-layout-v1';
  const PREFS='forest-studio-preferences-v1';
  const e=editorTr;
  let data=window.FOREST_BOOTSTRAP?.catalog,themes=window.FOREST_BOOTSTRAP?.themes||[];
  let scene,chosen=0,chosenSkin='normal',phase='7',filter='all',tool='place',selection=null,hover=null,drag=null,space=false;
  let geometry,view={width:0,height:0,fit:1,zoom:1,panX:0,panY:0},drawPending=false;
  let undoStack=[],redoStack=[],groundCanvas=null,groundKey='',toastTimer,syncBusy=false,revision='';
  const images=new Map(),masks=new Map();
  let randomMode=false,randomCandidates=[];
  function savePreferences(){
    if(!scene)return;
    try{localStorage.setItem(PREFS,JSON.stringify({chosen,chosenSkin,phase,filter,tool,randomMode,
      zoom:view.zoom,panX:view.panX,panY:view.panY,brush:$('brush-size').value,
      grid:$('show-grid').checked,background:$('export-background').value}));}catch(error){}
  }
  function restorePreferences(){
    let prefs;try{prefs=JSON.parse(localStorage.getItem(PREFS)||'null');}catch(error){return;}
    if(!prefs||typeof prefs!=='object')return;
    if(data.phases[prefs.chosen])chosen=Number(prefs.chosen);
    chosenSkin=prefs.chosenSkin==='christmas'&&stages(chosen,'christmas').length?'christmas':'normal';
    phase=stages(chosen,chosenSkin).includes(String(prefs.phase))?String(prefs.phase):mature(chosen,chosenSkin);
    filter=prefs.filter==='seasonal'?'seasonal':'all';
    document.querySelectorAll('[data-filter]').forEach(button=>{const active=button.dataset.filter===filter;button.classList.toggle('active',active);button.setAttribute('aria-selected',String(active));});
    randomMode=prefs.randomMode===true;
    if(['place','select','hand','erase','fill','remove-area'].includes(prefs.tool))setTool(prefs.tool);
    if(Number.isFinite(prefs.zoom))view.zoom=Math.max(.35,Math.min(6,prefs.zoom));
    if(Number.isFinite(prefs.panX))view.panX=prefs.panX;
    if(Number.isFinite(prefs.panY))view.panY=prefs.panY;
    if(['1','3','5'].includes(prefs.brush))$('brush-size').value=prefs.brush;
    $('show-grid').checked=prefs.grid===true;
    if(['transparent','black','cream'].includes(prefs.background))$('export-background').value=prefs.background;
  }
  const uid=()=>crypto.randomUUID?crypto.randomUUID():Date.now()+'-'+Math.random().toString(36).slice(2);
  const name=id=>{const meta=data?.metadata[id]||{},suffix={zh:'ZH',en:'EN',fr:'FR'}[forestLanguage];return meta['name'+suffix]||meta.nameEN||meta.nameZH||e('树 #')+id;};
  const phaseName=p=>p==='dead'?e('枯萎'):e('阶段 {n}',{n:p});
  const landName=skin=>FOREST_THEME_MESSAGES[forestLanguage]?.[skin.id]?.[0]||skin.name;
  const landDescription=skin=>FOREST_THEME_MESSAGES[forestLanguage]?.[skin.id]?.[1]||skin.description;
  let saveMessage='已自动保存';
  function notify(text){$('toast').textContent=e(text);$('toast').classList.add('show');clearTimeout(toastTimer);toastTimer=setTimeout(()=>$('toast').classList.remove('show'),3000);}
  function image(url){
    if(!url)return null;
    if(!images.has(url)){
      const img=new Image(),entry={img,state:'loading',promise:null};
      entry.promise=new Promise(resolve=>{img.onload=()=>{entry.state='ready';scheduleDraw();resolve(true);};img.onerror=()=>{entry.state='error';scheduleDraw();resolve(false);};});
      images.set(url,entry);img.src=window.FOREST_LOCAL_IMAGES?.[url.split('?')[0]]||url;
    }
    const entry=images.get(url);return entry.state==='ready'?entry.img:null;
  }
  function treeUrl(id,p,skin='normal'){
    // Product textures are higher-resolution artwork for the final growth stage.
    if(skin==='normal'&&(p==='product'||String(p)===mature(id))&&data.imagePaths[id+'_product'])return data.imagePaths[id+'_product'];
    const key=id+'_'+p;
    return skin==='christmas'?(data.imagePaths[key+'_christmas']||null):(data.imagePaths[key]||null);
  }
  function stages(id,skin='normal'){
    const result=(data.phases[id]||[]).map(String);
    if(data.imagePaths[id+'_dead'])result.push('dead');
    return skin==='christmas'?result.filter(p=>data.imagePaths[id+'_'+p+'_christmas']):result;
  }
  function mature(id,skin='normal'){const values=stages(id,skin).filter(p=>/^\d+$/.test(p));return values.at(-1)||'1';}
  function theme(){return themes.find(t=>t.id===scene.theme)||themes[0];}
  function save(){
    try{localStorage.setItem(STORE,JSON.stringify(scene));saveMessage='已自动保存';}
    catch(error){saveMessage='浏览器存储不可用，请保存布局';}
    $('save-state').textContent=e(saveMessage);
  }
  function commit(change){
    const before=JSON.stringify(scene);change();remember(before);
  }
  function remember(before){
    if(JSON.stringify(scene)===before)return;
    undoStack.push(before);if(undoStack.length>80)undoStack.shift();redoStack=[];save();refreshScene();
  }
  function history(back){
    const source=back?undoStack:redoStack,target=back?redoStack:undoStack;
    if(!source.length)return;
    target.push(JSON.stringify(scene));scene=JSON.parse(source.pop());selection=null;groundKey='';save();refreshScene();renderLibrary();renderStages();renderThemes();
  }
  function refreshScene(){
    for(const tree of scene.trees)if(tree.phase==='product')tree.phase=mature(tree.id,tree.skin);
    geometry=C.geometry(scene.size);
    view.fit=Math.max(.01,Math.min((view.width-64)/geometry.width,(view.height-84)/geometry.height));
    $('forest-title').value=scene.title;$('scene-title').textContent=scene.title||e('我的森林');
    $('placed-count').textContent=e('{n} 棵树',{n:scene.trees.length});$('land-count').textContent=e('{n} × {n} 地皮',{n:scene.size});
    $('size-label').textContent=scene.size+' × '+scene.size;$('land-size').value=scene.size;
    $('empty-help').hidden=scene.trees.length!==0;$('undo').disabled=!undoStack.length;$('redo').disabled=!redoStack.length;
    updateInspector();scheduleDraw();
  }
  function fitView(){view.zoom=1;view.panX=0;view.panY=0;scheduleDraw();}
  function transform(){const scale=view.fit*view.zoom;return {scale,x:(view.width-geometry.width*scale)/2+view.panX,y:(view.height-geometry.height*scale)/2+view.panY-5};}
  function world(clientX,clientY){const r=canvas.getBoundingClientRect(),t=transform();return {x:(clientX-r.left-t.x)/t.scale,y:(clientY-r.top-t.y)/t.scale};}
  function resize(){
    const r=canvas.getBoundingClientRect(),dpr=Math.min(devicePixelRatio||1,2);
    view.width=r.width;view.height=r.height;canvas.width=Math.round(r.width*dpr);canvas.height=Math.round(r.height*dpr);
    if(scene)refreshScene();
  }
  function scheduleDraw(){if(!drawPending){drawPending=true;requestAnimationFrame(()=>{drawPending=false;if(scene)draw();});}}
  function tilePath(target,row,col){const p=C.tile(geometry,row,col);target.beginPath();target.moveTo(p.x+100,p.y);target.lineTo(p.x+200,p.y+50);target.lineTo(p.x+100,p.y+100);target.lineTo(p.x,p.y+50);target.closePath();}
  function buildGround(){
    const skin=theme();if(!skin)return null;
    const tile=image(skin.tile),left=image(skin.left),right=image(skin.right);
    if(!tile||!left||!right)return null;
    const key=scene.size+'-'+skin.id;
    if(groundCanvas&&groundKey===key)return groundCanvas;
    const ground=document.createElement('canvas');ground.width=geometry.width;ground.height=geometry.height;
    const target=ground.getContext('2d');target.imageSmoothingEnabled=true;target.imageSmoothingQuality='high';
    // Tile edges contain partially transparent pixels. Fill the whole land first,
    // then overlap the textures as GroundRectView does, so scaling cannot expose gaps.
    const sample=document.createElement('canvas');sample.width=tile.naturalWidth;sample.height=tile.naturalHeight;
    const sampler=sample.getContext('2d',{willReadFrequently:true});sampler.drawImage(tile,0,0);
    const color=sampler.getImageData(Math.floor(sample.width/2),Math.floor(sample.height/2),1,1).data;
    target.fillStyle=`rgb(${color[0]},${color[1]},${color[2]})`;
    target.beginPath();target.moveTo(geometry.originX,geometry.originY);
    target.lineTo(geometry.originX+scene.size*100,geometry.originY+scene.size*50);
    target.lineTo(geometry.originX,geometry.originY+scene.size*100);
    target.lineTo(geometry.originX-scene.size*100,geometry.originY+scene.size*50);target.closePath();target.fill();
    for(let row=0;row<scene.size;row++)for(let col=0;col<scene.size;col++){
      const p=C.tile(geometry,row,col);target.drawImage(tile,p.x-1.2,p.y-1.2,202.4,102.4);
    }
    const x=geometry.originX-scene.size*100,y=geometry.originY+scene.size*50;
    for(let i=0;i<scene.size;i++)target.drawImage(left,x+i*100,y+i*50-1,101.5,150);
    for(let i=0;i<scene.size;i++)target.drawImage(right,geometry.originX+(scene.size-1-i)*100,y+i*50-1,101.5,150);
    groundCanvas=ground;groundKey=key;return ground;
  }
  function renderTree(target,tree,opacity=1){
    const url=treeUrl(tree.id,tree.phase,tree.skin),img=image(url),r=C.treeRect(geometry,tree);
    target.save();target.globalAlpha=opacity;
    if(img){
      const shadow=image('assets/ground/tree-shadow.png');
      if(shadow)target.drawImage(shadow,r.x,r.y+125,160,50);
      target.drawImage(img,r.x,r.y,r.width,r.height);
    }else{
      const p=C.center(geometry,tree.row,tree.col);target.fillStyle='#72935c';target.font='16px sans-serif';target.textAlign='center';target.fillText(url?e('载入中…'):e('图片缺失'),p.x,p.y);
    }
    target.restore();
  }
  function renderForest(target,overlays){
    const ground=buildGround();if(ground)target.drawImage(ground,0,0);
    if(overlays&&$('show-grid').checked){
      target.save();target.strokeStyle=scene.theme==='xmas'?'#7a9da533':'#46612629';target.lineWidth=.9;
      for(let r=0;r<scene.size;r++)for(let c=0;c<scene.size;c++){tilePath(target,r,c);target.stroke();}target.restore();
    }
    if(overlays&&selection){const tree=scene.trees.find(t=>t.uid===selection);if(tree){tilePath(target,tree.row,tree.col);target.fillStyle='#ffffff5a';target.fill();target.strokeStyle='#ffffff';target.lineWidth=3;target.stroke();}}
    if(overlays&&drag?.kind==='rectangle'){
      const cells=C.rectangleCells(scene.size,drag.start,drag.end);target.fillStyle=drag.erase?'#df776956':'#f7ffcb85';target.strokeStyle=drag.erase?'#d37969':'#fff';target.lineWidth=1.5;
      for(const cell of cells){tilePath(target,cell.row,cell.col);target.fill();target.stroke();}
    }
    if(overlays&&hover&&['place','erase'].includes(tool)&&Number($('brush-size').value)>1){
      target.lineWidth=1.5;target.strokeStyle='#ffffffa0';
      for(const cell of C.brushCells(scene.size,hover,Number($('brush-size').value))){target.fillStyle=tool==='erase'?'#df77694a':C.occupied(scene,cell.row,cell.col)?'#82905b20':'#ffffff65';tilePath(target,cell.row,cell.col);target.fill();target.stroke();}
    }
    for(const tree of C.depth(scene.trees))renderTree(target,tree,(overlays&&drag?.kind==='tree'&&drag.uid===tree.uid&&drag.moved) ? .4 : 1);
    if(overlays&&hover&&tool!=='hand'&&drag?.kind!=='rectangle'){
      const occupied=C.occupied(scene,hover.row,hover.col,drag?.uid),valid=!occupied;
      tilePath(target,hover.row,hover.col);target.fillStyle=tool==='erase'?'#d86f6845':valid?'#ffffff70':'#e36e6855';target.fill();target.strokeStyle=valid?'#fff':'#c66559';target.lineWidth=2.5;target.stroke();
      if(valid&&(!randomMode||drag?.kind==='tree'||drag?.kind==='palette')&&(tool==='place'||drag?.kind==='tree'||drag?.kind==='palette')){
        const moving=drag?.kind==='tree'?scene.trees.find(t=>t.uid===drag.uid):null;
        renderTree(target,{...(moving||{id:chosen,phase,skin:chosenSkin}),row:hover.row,col:hover.col},.65);
      }
    }
  }
  function draw(){
    const dpr=canvas.width/view.width||1;ctx.setTransform(dpr,0,0,dpr,0,0);ctx.clearRect(0,0,view.width,view.height);
    const t=transform();ctx.save();ctx.translate(t.x,t.y);ctx.scale(t.scale,t.scale);renderForest(ctx,true);ctx.restore();
    $('zoom-label').textContent=Math.round(view.zoom*100)+'%';
  }
  function alphaHit(img,x,y){
    const key=img.src;
    if(!masks.has(key)){
      const mask=document.createElement('canvas');mask.width=96;mask.height=96;
      const m=mask.getContext('2d',{willReadFrequently:true});m.drawImage(img,0,0,96,96);
      try{masks.set(key,m.getImageData(0,0,96,96).data);}catch(error){return true;}
    }
    const ix=Math.max(0,Math.min(95,Math.floor(x*96))),iy=Math.max(0,Math.min(95,Math.floor(y*96)));
    return masks.get(key)[(iy*96+ix)*4+3]>26;
  }
  function hitTree(point){
    for(const tree of C.depth(scene.trees).reverse()){
      const r=C.treeRect(geometry,tree);
      if(point.x<r.x||point.y<r.y||point.x>=r.x+r.width||point.y>=r.y+r.height)continue;
      const img=image(treeUrl(tree.id,tree.phase,tree.skin));if(img&&alphaHit(img,(point.x-r.x)/r.width,(point.y-r.y)/r.height))return tree;
    }
    return null;
  }
  function setTool(value){
    tool=value;hover=null;document.querySelectorAll('[data-tool]').forEach(button=>{button.classList.toggle('active',button.dataset.tool===tool);button.setAttribute('aria-pressed',String(button.dataset.tool===tool));});
    canvas.style.cursor=tool==='hand'?'grab':tool==='select'?'default':tool==='erase'?'not-allowed':'crosshair';
    $('interaction-hint').textContent={place:randomMode?e('按住涂抹随机种植 · 只种阶段 4+ 的树'):e('按住鼠标涂抹种植 · 已占用地块自动跳过'),select:e('点击选中树木 · 拖到空地移动 · Delete 移除'),hand:e('拖动画布平移 · 滚轮缩放 · 适应画布还原'),erase:e('按住鼠标经过地块，连续删除 · 一笔可撤销'),fill:e('拖出一个地块区域，批量种植空位'), 'remove-area':e('拖出一个地块区域，批量删除区域内的树')}[tool];scheduleDraw();
  }
  function chooseTree(id){randomMode=false;updateRandomMode();chosen=id;chosenSkin=filter==='seasonal'?'christmas':'normal';phase=mature(id,chosenSkin);setTool('place');renderLibrary();renderStages();}
  function renderLibrary(){
    const box=$('tree-library'),scroll=box.scrollTop,kw=$('tree-search').value.trim().toLowerCase();box.replaceChildren();
    const rows=data.trees.filter(t=>(filter!=='seasonal'||t[5])&&(!kw||[t[0],t[1],t[2],data.metadata[t[0]]?.nameFR].some(v=>String(v||'').toLowerCase().includes(kw))));
    $('library-count').textContent=rows.length;
    for(const t of rows){
      const button=document.createElement('button');button.className='tree-card'+(t[0]===chosen?' active':'');button.setAttribute('aria-label',e('选择树种 {name}',{name:name(t[0])}));button.setAttribute('aria-pressed',String(t[0]===chosen));
      const skin=filter==='seasonal'?'christmas':'normal';
      const img=document.createElement('img');img.loading='lazy';img.alt=name(t[0])+(skin==='christmas'?e(' · 圣诞版'):'');img.src=treeUrl(t[0],mature(t[0],skin),skin);
      const label=document.createElement('span');label.textContent=name(t[0]);button.append(img,label);button.title=name(t[0])+' · ID '+t[0];button.onclick=()=>chooseTree(t[0]);box.append(button);
    }
    if(!rows.length){const empty=document.createElement('p');empty.className='microcopy';empty.textContent=e('没有找到匹配的树种');box.append(empty);}
    box.scrollTop=scroll;
  }
  function renderStages(){
    $('chosen-name').textContent=name(chosen);$('chosen-id').textContent='#'+chosen;
    $('tree-skin').value=chosenSkin;$('tree-skin').querySelector('[value="christmas"]').disabled=!stages(chosen,'christmas').length;
    const box=$('stage-list'),scroll=box.scrollLeft;box.replaceChildren();
    for(const p of stages(chosen,chosenSkin)){
      const button=document.createElement('button');button.className='stage-card'+(p===phase?' active':'');button.draggable=true;button.setAttribute('aria-label',e('选择并拖动 {name} {phase}',{name:name(chosen),phase:phaseName(p)}));button.setAttribute('aria-pressed',String(p===phase));
      const img=document.createElement('img');img.src=treeUrl(chosen,p,chosenSkin);img.alt=phaseName(p)+(chosenSkin==='christmas'?e(' 圣诞版'):'');
      const label=document.createElement('span');label.textContent=phaseName(p);button.append(img,label);
      button.onclick=()=>{randomMode=false;updateRandomMode();phase=p;setTool('place');renderStages();};
      button.addEventListener('dragstart',event=>{
        randomMode=false;updateRandomMode();phase=p;setTool('place');drag={kind:'palette',moved:true};
        event.dataTransfer.setData('application/x-forest-tree',JSON.stringify({id:chosen,phase:p,skin:chosenSkin}));event.dataTransfer.effectAllowed='copy';
        if(img.complete)event.dataTransfer.setDragImage(img,30,45);
      });
      button.addEventListener('dragend',()=>{drag=null;hover=null;renderStages();scheduleDraw();});box.append(button);
    }
    box.scrollLeft=scroll;
  }
  function renderThemes(){
    const box=$('theme-list');box.replaceChildren();
    for(const skin of themes){
      const button=document.createElement('button');button.className='theme-card'+(skin.id===scene.theme?' active':'');button.title=landDescription(skin);button.setAttribute('aria-label',e('地皮主题 {name}',{name:landName(skin)}));button.setAttribute('aria-pressed',String(skin.id===scene.theme));
      const img=document.createElement('img');img.src=skin.tile;img.alt=landName(skin);
      const text=document.createElement('span');text.textContent=landName(skin);button.append(img,text);
      button.onclick=()=>{commit(()=>{scene.theme=skin.id;});groundKey='';renderThemes();renderLibrary();renderStages();scheduleDraw();notify(e('已切换为{name}，树木位置保持不变',{name:landName(skin)}));};box.append(button);
    }
  }
  function updateInspector(){
    const tree=scene.trees.find(t=>t.uid===selection);
    $('selection-empty').hidden=!!tree;$('selection-details').hidden=!tree;$('selection-cell').textContent=tree?'#'+tree.id:'—';
    if(!tree)return;
    $('selection-img').src=treeUrl(tree.id,tree.phase,tree.skin)||'';$('selection-img').alt=name(tree.id);
    $('selection-name').textContent=name(tree.id);$('selection-position').textContent=e('第 {row} 行 · 第 {col} 列',{row:tree.row+1,col:tree.col+1});
    const select=$('selection-phase');select.replaceChildren();
    $('selection-skin').value=tree.skin||'normal';$('selection-skin').querySelector('[value="christmas"]').disabled=!stages(tree.id,'christmas').length;
    for(const p of stages(tree.id,tree.skin)){const option=document.createElement('option');option.value=p;option.textContent=phaseName(p);select.append(option);}select.value=tree.phase;
  }
  function selectTree(tree){selection=tree?.uid||null;updateInspector();scheduleDraw();}
  function deleteTree(tree){if(!tree)return;commit(()=>{scene.trees=scene.trees.filter(t=>t.uid!==tree.uid);selection=null;});}
  function placeAt(cell,moveUid){
    if(!cell){notify(e('请放在地皮范围内'));return;}
    let result;commit(()=>{result=C.place(scene,{uid:uid(),id:chosen,phase,skin:chosenSkin},cell.row,cell.col,moveUid);});
    if(!result.ok)notify(result.reason);else{selection=result.uid;updateInspector();scheduleDraw();}
  }
  function updateRandomMode(){
    randomCandidates=C.randomPool(data,$('random-scope').value);
    $('random-mode').classList.toggle('active',randomMode);$('random-mode').setAttribute('aria-pressed',String(randomMode));
    $('random-scope-label').hidden=!randomMode;$('random-info').hidden=!randomMode;
    document.querySelector('.stage-picker').hidden=randomMode;
    $('random-info').textContent=e('{n} 个可用树种，每格独立随机树种和阶段（≥4），不含枯萎。',{n:randomCandidates.length});
    $('fill-empty').textContent=randomMode?e('用随机树种种满空地'):e('用当前树种 / 阶段种满空地');
  }
  function createPlant(){const tree=randomMode?C.randomTree(randomCandidates):{id:chosen,phase,skin:chosenSkin};return tree?{uid:uid(),...tree}:null;}
  function canPlant(){if(randomMode&&!randomCandidates.length){notify(e('这个外观范围没有阶段 4 及以上的可用树种'));return false;}return true;}
  function applyStrokeCells(cells){
    const todo=[];
    for(const cell of cells)for(const c of C.brushCells(scene.size,cell,Number($('brush-size').value))){const key=c.row+','+c.col;if(!drag.visited.has(key)){drag.visited.add(key);todo.push(c);}}
    drag.changed+=C.paintCells(scene,todo,drag.erase,createPlant);
    $('placed-count').textContent=e('{n} 棵树',{n:scene.trees.length});$('empty-help').hidden=scene.trees.length!==0;scheduleDraw();
  }
  function finishStroke(){
    if(drag?.kind!=='stroke')return;
    const current=drag;drag=null;remember(current.before);
    if(current.changed)notify(e(current.erase?'已连续删除 {n} 棵树，可一次撤销':'已连续种植 {n} 棵树，可一次撤销',{n:current.changed}));
  }
  function updateHover(event){
    const point=world(event.clientX,event.clientY);hover=C.cellAt(geometry,point.x,point.y);scheduleDraw();return point;
  }
  function setHoverLabel(event,tree){
    const label=$('hover-label');if(!tree||drag){label.hidden=true;return;}
    label.textContent=name(tree.id)+' · '+phaseName(tree.phase);const r=canvas.getBoundingClientRect();
    label.style.left=Math.max(8,Math.min(event.clientX-r.left+14,view.width-210))+'px';label.style.top=Math.max(8,event.clientY-r.top-42)+'px';label.hidden=false;
  }
  canvas.addEventListener('pointerdown',event=>{
    if(event.button!==0&&event.button!==1)return;canvas.focus();event.preventDefault();
    const point=world(event.clientX,event.clientY);
    if(tool==='hand'||space||event.button===1){drag={kind:'pan',x:event.clientX,y:event.clientY,panX:view.panX,panY:view.panY};canvas.setPointerCapture(event.pointerId);return;}
    const cell=C.cellAt(geometry,point.x,point.y);
    if(tool==='fill'||tool==='remove-area'){
      if(!cell||(tool==='fill'&&!canPlant()))return;
      drag={kind:'rectangle',start:cell,end:cell,erase:tool==='remove-area'};hover=cell;canvas.setPointerCapture(event.pointerId);scheduleDraw();return;
    }
    if(tool==='place'||tool==='erase'){
      if(tool==='place'&&!canPlant())return;
      selection=null;updateInspector();drag={kind:'stroke',before:JSON.stringify(scene),visited:new Set(),erase:tool==='erase',last:point,changed:0};
      applyStrokeCells(cell?[cell]:[]);canvas.setPointerCapture(event.pointerId);return;
    }
    const tree=hitTree(point);
    if(tree){selectTree(tree);drag={kind:'tree',uid:tree.uid,x:event.clientX,y:event.clientY,moved:false};canvas.setPointerCapture(event.pointerId);return;}
    if(tool==='place')placeAt(C.cellAt(geometry,point.x,point.y));else selectTree(null);
  });
  canvas.addEventListener('pointermove',event=>{
    if(drag?.kind==='pan'){view.panX=drag.panX+event.clientX-drag.x;view.panY=drag.panY+event.clientY-drag.y;scheduleDraw();return;}
    const point=updateHover(event);
    if(drag?.kind==='stroke'){applyStrokeCells(C.traceCells(geometry,drag.last,point));drag.last=point;return;}
    if(drag?.kind==='rectangle'){if(hover)drag.end=hover;scheduleDraw();return;}
    if(drag?.kind==='tree'&&Math.hypot(event.clientX-drag.x,event.clientY-drag.y)>5)drag.moved=true;
    setHoverLabel(event,hitTree(point));
  });
  canvas.addEventListener('pointerup',event=>{
    if(drag?.kind==='stroke'){const point=world(event.clientX,event.clientY);applyStrokeCells(C.traceCells(geometry,drag.last,point));finishStroke();}
    if(drag?.kind==='rectangle'){
      const rectangle=drag;drag=null;let changed=0;commit(()=>{changed=C.paintCells(scene,C.rectangleCells(scene.size,rectangle.start,rectangle.end),rectangle.erase,createPlant);selection=null;});notify(e(rectangle.erase?'已批量删除 {n} 棵树，可一次撤销':'已批量种植 {n} 棵树，可一次撤销',{n:changed}));
    }
    if(drag?.kind==='tree'&&drag.moved){const point=world(event.clientX,event.clientY);placeAt(C.cellAt(geometry,point.x,point.y),drag.uid);}
    drag=null;if(canvas.hasPointerCapture(event.pointerId))canvas.releasePointerCapture(event.pointerId);scheduleDraw();
  });
  canvas.addEventListener('pointercancel',()=>{finishStroke();drag=null;hover=null;scheduleDraw();});
  canvas.addEventListener('pointerleave',()=>{if(!drag)hover=null;$('hover-label').hidden=true;scheduleDraw();});
  canvas.addEventListener('dragover',event=>{if(!event.dataTransfer.types.includes('application/x-forest-tree'))return;event.preventDefault();event.dataTransfer.dropEffect='copy';drag={kind:'palette',moved:true};updateHover(event);});
  canvas.addEventListener('dragleave',()=>{hover=null;scheduleDraw();});
  canvas.addEventListener('drop',event=>{
    event.preventDefault();try{
      const payload=JSON.parse(event.dataTransfer.getData('application/x-forest-tree'));
      if(!['normal','christmas'].includes(payload.skin)||!data.trees.some(t=>t[0]===payload.id)||!stages(payload.id,payload.skin).includes(String(payload.phase)))throw new Error(e('树种或阶段不可用'));
      chosen=payload.id;chosenSkin=payload.skin;phase=String(payload.phase);const point=world(event.clientX,event.clientY);placeAt(C.cellAt(geometry,point.x,point.y));renderStages();
    }catch(error){notify(error.message||e('无法放置这棵树'));}drag=null;hover=null;scheduleDraw();
  });
  function zoom(factor,point){
    const old=transform();view.zoom=Math.max(.35,Math.min(6,view.zoom*factor));
    if(point){const next=transform(),x=(point.x-old.x)/old.scale,y=(point.y-old.y)/old.scale;view.panX+=point.x-(next.x+x*next.scale);view.panY+=point.y-(next.y+y*next.scale);}
    scheduleDraw();
  }
  canvas.addEventListener('wheel',event=>{event.preventDefault();const rect=canvas.getBoundingClientRect();zoom(Math.exp(-event.deltaY*.0015),{x:event.clientX-rect.left,y:event.clientY-rect.top});},{passive:false});
  function example(){
    const result={version:1,title:'花间小森林',size:12,theme:'default',trees:[]};
    const ids=[160,129,117,113,118,115,112,106,103,104,105,108];
    for(let row=0;row<12;row++)for(let col=0;col<12;col++){
      if((row===0&&col<2)||(col===0&&row<2)||(row===11&&col>8)||(row===5&&col===6)||(row===6&&col===5))continue;
      const id=ids[col%ids.length];if(!data.phases[id])continue;
      const growth=data.phases[id],forest=(data.metadata[id]?.phase?.forest||[]).filter(p=>data.imagePaths[id+'_'+p]);
      const choices=forest.length?forest:growth.slice(-4),stage=String(choices[row%choices.length]);
      result.trees.push({uid:uid(),id,phase:stage,skin:'normal',row,col});
    }
    return result;
  }
  function download(blob,filename){const url=URL.createObjectURL(blob),anchor=document.createElement('a');anchor.href=url;anchor.download=filename;anchor.click();setTimeout(()=>URL.revokeObjectURL(url),30000);}
  const filename=()=>((scene.title||e('我的森林')).replace(/[\\/:*?"<>|]/g,'_').slice(0,60));
  async function exportImage(){
    const button=$('export-image');button.disabled=true;button.textContent=e('正在绘制…');
    try{
      const snapshot=JSON.stringify(scene);
      const skin=theme(),urls=[skin.tile,skin.left,skin.right,'assets/ground/tree-shadow.png',...scene.trees.map(t=>treeUrl(t.id,t.phase,t.skin))];
      urls.filter(Boolean).forEach(image);await Promise.all(urls.filter(Boolean).map(url=>images.get(url).promise));
      if(JSON.stringify(scene)!==snapshot)throw new Error(e('画布已变化，请重新导出'));
      const missing=urls.filter(url=>!url||images.get(url)?.state!=='ready');if(missing.length)throw new Error(e('有 {n} 个贴图尚不可用，请检查资源后再导出',{n:missing.length}));
      const scale=Math.min(2.2,8192/Math.max(geometry.width,geometry.height)),output=document.createElement('canvas');
      output.width=Math.round(geometry.width*scale);output.height=Math.round(geometry.height*scale);
      const target=output.getContext('2d');target.scale(scale,scale);target.imageSmoothingQuality='high';
      const background=$('export-background').value;
      if(background!=='transparent'){target.fillStyle=background==='black'?'#000':'#f4f5ec';target.fillRect(0,0,geometry.width,geometry.height);}
      renderForest(target,false);
      const blob=await new Promise(resolve=>output.toBlob(resolve,'image/png'));if(!blob)throw new Error(e('图片过大，无法导出'));
      download(blob,filename()+'.png');notify(e('已导出 {w} × {h} PNG',{w:output.width,h:output.height}));
    }catch(error){notify(error.message);}finally{button.disabled=false;button.textContent=e('导出森林图')+' ↗';}
  }
  async function synchronize(){
    if(!['localhost','127.0.0.1','[::1]'].includes(location.hostname)||syncBusy||drag)return;syncBusy=true;
    try{
      const response=await fetch('/api/tree-data',{cache:'no-store'});if(!response.ok)throw new Error('unavailable');
      const next=await response.json();if(!next.trees?.length||!next.imagePaths||!next.metadata)throw new Error('invalid');
      if(next.revision!==revision){
        data=next;revision=next.revision;if(!data.phases[chosen]){chosen=data.trees[0][0];chosenSkin='normal';phase=mature(chosen);}else {if(chosenSkin==='christmas'&&!stages(chosen,'christmas').length)chosenSkin='normal';if(!stages(chosen,chosenSkin).includes(phase))phase=mature(chosen,chosenSkin);}
        masks.clear();renderLibrary();renderStages();updateInspector();updateRandomMode();scheduleDraw();
      }
      $('data-status').textContent=e('● 自动同步 · {n} 个树种 · 布局已保留',{n:data.trees.length});
    }catch(error){$('data-status').textContent=e('○ 保留当前资源 · 稍后自动重试');}finally{syncBusy=false;}
  }
  document.querySelectorAll('[data-tool]').forEach(button=>button.onclick=()=>setTool(button.dataset.tool));
  document.querySelectorAll('[data-filter]').forEach(button=>button.onclick=()=>{filter=button.dataset.filter;document.querySelectorAll('[data-filter]').forEach(b=>{b.classList.toggle('active',b===button);b.setAttribute('aria-selected',String(b===button));});if(filter==='seasonal'){chosenSkin='christmas';if(!stages(chosen,'christmas').length)chosen=data.trees.find(t=>t[5])[0];}else chosenSkin='normal';phase=mature(chosen,chosenSkin);renderLibrary();renderStages();});
  $('tree-skin').onchange=()=>{chosenSkin=$('tree-skin').value;phase=mature(chosen,chosenSkin);renderStages();setTool('place');};
  $('random-mode').onclick=()=>{randomMode=!randomMode;updateRandomMode();setTool('place');};
  $('random-scope').onchange=updateRandomMode;
  $('fill-empty').onclick=()=>{if(!canPlant())return;let changed=0;commit(()=>{changed=C.paintCells(scene,C.rectangleCells(scene.size,{row:0,col:0},{row:scene.size-1,col:scene.size-1}),false,createPlant);selection=null;});notify(e('已种植 {n} 棵树，可一次撤销',{n:changed}));};
  $('tree-search').addEventListener('input',renderLibrary);$('show-grid').onchange=scheduleDraw;
  $('undo').onclick=()=>history(true);$('redo').onclick=()=>history(false);
  $('zoom-in').onclick=()=>zoom(1.25);$('zoom-out').onclick=()=>zoom(.8);$('fit-view').onclick=fitView;
  $('forest-title').oninput=()=>{scene.title=$('forest-title').value;$('scene-title').textContent=scene.title||e('我的森林');save();};
  $('apply-size').onclick=()=>{
    const size=Number($('land-size').value);if(!Number.isInteger(size)||size<3||size>32){notify(e('地皮边长请输入 3–32 的整数'));return;}
    const removed=scene.trees.filter(t=>t.row>=size||t.col>=size).length;
    commit(()=>{scene.size=size;scene.trees=scene.trees.filter(t=>t.row<size&&t.col<size);});groundKey='';fitView();if(removed)notify(e('超出边界的 {n} 棵树已移除，可撤销恢复',{n:removed}));
  };
  $('selection-phase').onchange=()=>{const tree=scene.trees.find(t=>t.uid===selection);if(tree)commit(()=>{tree.phase=$('selection-phase').value;});};
  $('selection-skin').onchange=()=>{const tree=scene.trees.find(t=>t.uid===selection);if(tree)commit(()=>{tree.skin=$('selection-skin').value;if(!stages(tree.id,tree.skin).includes(tree.phase))tree.phase=mature(tree.id,tree.skin);});};
  $('delete-selected').onclick=()=>deleteTree(scene.trees.find(t=>t.uid===selection));
  $('load-example').onclick=()=>{commit(()=>{scene=example();selection=null;});groundKey='';fitView();renderThemes();renderLibrary();renderStages();notify(e('已载入示例森林，可撤销恢复之前的布局'));};
  $('clear-forest').onclick=()=>{commit(()=>{scene.trees=[];selection=null;});notify(e('地皮已清空，可撤销恢复'));};
  $('export-layout').onclick=()=>download(new Blob([JSON.stringify(scene,null,2)],{type:'application/json'}),filename()+'.json');
  $('import-layout').onclick=()=>$('layout-file').click();
  $('layout-file').onchange=async event=>{
    const file=event.target.files[0];if(!file)return;
    try{if(file.size>2e6)throw new Error(e('布局文件不能超过 2 MB'));const next=C.validateScene(JSON.parse(await file.text()),themes.map(t=>t.id));commit(()=>{scene=next;selection=null;});groundKey='';fitView();renderThemes();renderLibrary();renderStages();notify(e('布局已导入，缺失的贴图会显示提示'));}catch(error){notify(e('导入失败：{reason}',{reason:e(error.message)}));}event.target.value='';
  };
  $('export-image').onclick=exportImage;
  document.addEventListener('keydown',event=>{
    if(['INPUT','SELECT','TEXTAREA'].includes(event.target.tagName))return;
    if((event.ctrlKey||event.metaKey)&&event.key.toLowerCase()==='z'){event.preventDefault();finishStroke();history(!event.shiftKey);return;}
    if((event.ctrlKey||event.metaKey)&&event.key.toLowerCase()==='y'){event.preventDefault();history(false);return;}
    if(event.code==='Space'){event.preventDefault();space=true;canvas.style.cursor='grab';return;}
    if(event.key==='Delete'||event.key==='Backspace'){event.preventDefault();deleteTree(scene.trees.find(t=>t.uid===selection));return;}
    if(event.key==='Escape'){if(drag?.kind==='stroke'){scene=JSON.parse(drag.before);save();refreshScene();}drag=null;hover=null;selectTree(null);return;}
    const shortcuts={b:'place',v:'select',h:'hand',e:'erase',r:'fill',x:'remove-area'};if(shortcuts[event.key.toLowerCase()])setTool(shortcuts[event.key.toLowerCase()]);
  });
  document.addEventListener('keyup',event=>{if(event.code==='Space'){space=false;canvas.style.cursor=tool==='hand'?'grab':tool==='select'?'default':'crosshair';}});
  window.addEventListener('blur',()=>{space=false;finishStroke();drag=null;hover=null;scheduleDraw();});
  window.addEventListener('pagehide',()=>{if(scene){save();savePreferences();}});
  function applyEditorLanguage(){
    applyEditorStaticLanguage();
    if(!scene)return;
    $('save-state').textContent=e(saveMessage);
    $('export-image').textContent=e($('export-image').disabled?'正在绘制…':'导出森林图')+' ↗';
    renderLibrary();renderStages();renderThemes();updateRandomMode();refreshScene();setTool(tool);
    $('hover-label').hidden=true;$('toast').classList.remove('show');
  }
  $('editor-language').onchange=event=>{
    if(!Object.hasOwn(FOREST_MESSAGES,event.target.value))return;
    forestLanguage=event.target.value;
    try{localStorage.setItem('forest-language',forestLanguage);}catch(error){}
    applyEditorLanguage();
  };
  function syncLanguage(){const next=readForestLanguage();if(next!==forestLanguage){forestLanguage=next;applyEditorLanguage();}}
  window.addEventListener('storage',event=>{if(event.key==='forest-language'||event.key===null)syncLanguage();});
  window.addEventListener('pageshow',syncLanguage);
  document.addEventListener('visibilitychange',()=>{if(!document.hidden)syncLanguage();});
  document.addEventListener('visibilitychange',()=>{if(document.hidden&&scene){save();savePreferences();}});
  for(const event of ['click','change','pointerup'])document.addEventListener(event,()=>{setTimeout(savePreferences,0);});
  async function init(){
    try{
      if(!data||!themes.length)throw new Error(e('资源索引缺失，请运行准备脚本'));
      let saved=null;try{const raw=localStorage.getItem(STORE);if(raw)saved=C.validateScene(JSON.parse(raw),themes.map(t=>t.id));}catch(error){notify(e('已保存的布局无法读取，已载入示例'));}
      scene=saved||example();chosen=data.phases[117]?117:data.trees[0][0];phase=mature(chosen);geometry=C.geometry(scene.size);
      restorePreferences();
      new ResizeObserver(resize).observe(canvas);resize();renderLibrary();renderStages();renderThemes();updateRandomMode();refreshScene();save();
      applyEditorLanguage();
      if(['localhost','127.0.0.1','[::1]'].includes(location.hostname)){await synchronize();setInterval(synchronize,5000);document.addEventListener('visibilitychange',()=>{if(!document.hidden)synchronize();});}
    }catch(error){$('data-status').textContent=error.message;notify(error.message);}
  }
  init();
})();
