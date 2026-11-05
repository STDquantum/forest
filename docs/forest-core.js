(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;else root.ForestCore=api;})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';
  const TILE_W=200,TILE_H=100;
  function geometry(size){return {size,width:size*TILE_W+20,height:(size+2.5)*TILE_H,originX:size*TILE_W/2+10,originY:150};}
  function tile(g,row,col){return {x:g.originX+(col-row)*100-100,y:g.originY+(row+col)*50};}
  function cellAt(g,x,y){const dx=(x-g.originX)/100,dy=(y-g.originY)/50,col=Math.floor((dx+dy)/2),row=Math.floor((dy-dx)/2);return row>=0&&col>=0&&row<g.size&&col<g.size?{row,col}:null;}
  function center(g,row,col){const p=tile(g,row,col);return {x:p.x+100,y:p.y+50};}
  function treeRect(g,tree){const p=tile(g,tree.row,tree.col);return {x:p.x+20,y:p.y+75-160,width:160,height:160};}
  // getForest.py traverses columns within each row when compositing trees.
  function depth(trees){return [...trees].sort((a,b)=>a.row-b.row||a.col-b.col);}
  function occupied(scene,row,col,except){return scene.trees.find(tree=>tree.row===row&&tree.col===col&&tree.uid!==except);}
  function place(scene,tree,row,col,moveUid){
    if(!Number.isInteger(row)||!Number.isInteger(col)||row<0||col<0||row>=scene.size||col>=scene.size)return {ok:false,reason:'请放在地皮范围内'};
    if(occupied(scene,row,col,moveUid))return {ok:false,reason:'这块地已经有树了，请选择空地'};
    if(moveUid){const current=scene.trees.find(t=>t.uid===moveUid);if(!current)return {ok:false,reason:'找不到这棵树'};current.row=row;current.col=col;return {ok:true,uid:moveUid};}
    scene.trees.push({...tree,row,col});return {ok:true,uid:tree.uid};
  }
  function diagonal(cells,size){
    if(cells.length!==size)return false;
    const sorted=[...cells].sort((a,b)=>a.row-b.row);
    return sorted.every((p,i)=>p.row===i&&p.col===i)||sorted.every((p,i)=>p.row===i&&p.col===size-1-i);
  }
  function decorationCells(scene,seed=scene.size*31+scene.trees.length*7,keep=[]){
    const limit=scene.decorationCount??10,occupied=new Set(scene.trees.map(t=>t.row+','+t.col)),seen=new Set();
    const valid=keep.filter(p=>{const k=p.row+','+p.col;if(!Number.isInteger(p.row)||!Number.isInteger(p.col)||p.row<0||p.col<0||p.row>=scene.size||p.col>=scene.size||occupied.has(k)||seen.has(k))return false;seen.add(k);return true;}).slice(0,limit);
    const empty=[];for(let row=0;row<scene.size;row++)for(let col=0;col<scene.size;col++)if(!occupied.has(row+','+col)&&!seen.has(row+','+col))empty.push({row,col});
    for(let attempt=0;attempt<10;attempt++){
      const shuffled=[...empty];let n=(seed+attempt)%233280;
      for(let i=shuffled.length-1;i>0;i--){n=(n*9301+49297)%233280;const j=Math.floor(n/233280*(i+1));[shuffled[i],shuffled[j]]=[shuffled[j],shuffled[i]];}
      const result=valid.concat(shuffled.slice(0,Math.max(0,limit-valid.length)));
      if(!diagonal(result,scene.size))return result;
    }
    const fallback=valid.concat(empty.slice(0,Math.max(0,limit-valid.length)));
    if(diagonal(fallback,scene.size))fallback.pop();
    return fallback;
  }
  function moveDecoration(scene,from,to){
    if(!to||!Number.isInteger(to.row)||!Number.isInteger(to.col)||to.row<0||to.col<0||to.row>=scene.size||to.col>=scene.size||occupied(scene,to.row,to.col))return false;
    const cells=scene.decorations||decorationCells(scene),index=cells.findIndex(p=>p.row===from.row&&p.col===from.col);
    if(index<0||cells.some((p,i)=>i!==index&&p.row===to.row&&p.col===to.col))return false;
    const next=cells.map((p,i)=>i===index?{row:to.row,col:to.col}:p);if(diagonal(next,scene.size))return false;
    scene.decorations=next;return true;
  }
  function validateScene(input,themes){
    if(!input||input.version!==1||!Number.isInteger(input.size)||input.size<3||input.size>32||!Array.isArray(input.trees)||input.trees.length>input.size**2)throw new Error('布局格式不正确，地皮边长应为 3–32 格');
    if(!themes.includes(input.theme))throw new Error('布局使用了未知地皮主题');
    const positions=new Set(),ids=new Set();
    const trees=input.trees.map((t,index)=>{
      if(!t||!Number.isInteger(t.id)||t.id<0||!Number.isInteger(t.row)||!Number.isInteger(t.col)||t.row<0||t.col<0||t.row>=input.size||t.col>=input.size||! /^(?:[1-9]\d?|dead|product)$/.test(String(t.phase)))throw new Error('布局中有无效的树种、阶段或坐标');
      const pos=t.row+','+t.col;if(positions.has(pos))throw new Error('布局中有重叠地块');positions.add(pos);
      const uid=typeof t.uid==='string'&&t.uid.length<100?t.uid:'import-'+index;if(ids.has(uid))throw new Error('布局中有重复的树木编号');ids.add(uid);
      if(t.skin!==undefined&&!['normal','christmas'].includes(t.skin))throw new Error('布局中有未知的树木外观');
      return {uid,id:t.id,phase:String(t.phase),skin:t.skin||'normal',row:t.row,col:t.col};
    });
    const result={version:1,title:typeof input.title==='string'?input.title.slice(0,80):'我的森林',size:input.size,theme:input.theme,trees};
    if(input.decorationCount!==undefined){
      if(!Number.isInteger(input.decorationCount)||input.decorationCount<0||input.decorationCount>1024)throw new Error('装饰数量应为 0–1024 的整数');
      result.decorationCount=input.decorationCount;
    }
    if(input.decorations!==undefined){
      if(!Array.isArray(input.decorations)||input.decorations.length>(result.decorationCount??10))throw new Error('布局中的装饰位置无效');
      const used=new Set();result.decorations=input.decorations.map(p=>{const key=p?.row+','+p?.col;if(!p||!Number.isInteger(p.row)||!Number.isInteger(p.col)||p.row<0||p.col<0||p.row>=input.size||p.col>=input.size||positions.has(key)||used.has(key))throw new Error('布局中的装饰位置无效');used.add(key);return {row:p.row,col:p.col};});
      if(diagonal(result.decorations,input.size))throw new Error('布局中的装饰位置无效');
    }
    return result;
  }
  function brushCells(size,cell,width=1){
    if(!cell)return [];
    const out=[],radius=Math.floor(width/2);
    for(let row=cell.row-radius;row<=cell.row+radius;row++)for(let col=cell.col-radius;col<=cell.col+radius;col++)if(row>=0&&col>=0&&row<size&&col<size)out.push({row,col});
    return out;
  }
  function rectangleCells(size,a,b){
    if(!a||!b)return [];
    const out=[];
    for(let row=Math.max(0,Math.min(a.row,b.row));row<=Math.min(size-1,Math.max(a.row,b.row));row++)for(let col=Math.max(0,Math.min(a.col,b.col));col<=Math.min(size-1,Math.max(a.col,b.col));col++)out.push({row,col});
    return out;
  }
  function traceCells(g,a,b){
    const steps=Math.min(2048,Math.max(1,Math.ceil((Math.abs(b.x-a.x)/100+Math.abs(b.y-a.y)/50)*3))),seen=new Set(),out=[];
    for(let i=0;i<=steps;i++){const t=i/steps,cell=cellAt(g,a.x+(b.x-a.x)*t,a.y+(b.y-a.y)*t);if(cell){const key=cell.row+','+cell.col;if(!seen.has(key)){seen.add(key);out.push(cell);}}}
    return out;
  }
  function randomPool(catalog,scope='normal'){
    const skins=scope==='mixed'?['normal','christmas']:[scope],out=[];
    for(const tree of catalog.trees){const id=tree[0],options=[];
      for(const skin of skins)for(const p of catalog.phases[id]||[])if(Number.isInteger(p)&&p>=4&&catalog.imagePaths[id+'_'+p+(skin==='christmas'?'_christmas':'')])options.push({phase:String(p),skin});
      if(options.length)out.push({id,options});
    }
    return out;
  }
  function randomTree(pool,random=Math.random){if(!pool.length)return null;const tree=pool[Math.min(pool.length-1,Math.floor(random()*pool.length))],variant=tree.options[Math.min(tree.options.length-1,Math.floor(random()*tree.options.length))];return {id:tree.id,...variant};}
  function paintCells(scene,cells,erase,create){
    const seen=new Set(),unique=cells.filter(c=>{const k=c.row+','+c.col;if(seen.has(k)||c.row<0||c.col<0||c.row>=scene.size||c.col>=scene.size)return false;seen.add(k);return true;});
    if(erase){const before=scene.trees.length;scene.trees=scene.trees.filter(t=>!seen.has(t.row+','+t.col));return before-scene.trees.length;}
    const filled=new Set(scene.trees.map(t=>t.row+','+t.col));let changed=0;
    for(const cell of unique){const key=cell.row+','+cell.col;if(filled.has(key))continue;const tree=create();if(!tree)continue;scene.trees.push({...tree,row:cell.row,col:cell.col});filled.add(key);changed++;}
    return changed;
  }
  return {TILE_W,TILE_H,geometry,tile,center,cellAt,treeRect,depth,occupied,place,validateScene,brushCells,rectangleCells,traceCells,randomPool,randomTree,paintCells,diagonal,decorationCells,moveDecoration};
});
