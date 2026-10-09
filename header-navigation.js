// Native disclosure keeps keyboard support and navigation available without JS.
export function activateHeaderNavigation(root){
 const menu=root.querySelector('header .header-navigation');if(!menu)return;
 const narrow=matchMedia('(max-width:1199px)');
 const adapt=()=>{menu.open=!narrow.matches;};adapt();narrow.addEventListener('change',adapt);
 menu.addEventListener('click',event=>{if(narrow.matches&&event.target.closest('a'))menu.open=false;});
 root.addEventListener('click',event=>{if(narrow.matches&&menu.open&&!menu.contains(event.target))menu.open=false;});
 root.addEventListener('keydown',event=>{if(event.key==='Escape'&&narrow.matches&&menu.open){menu.open=false;menu.querySelector('summary').focus();}});
}
