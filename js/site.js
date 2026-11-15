(function(){
  var nav=document.getElementById('nav'),bg=document.getElementById('heroBg'),hh=document.getElementById('heroHeadline');
  function onScroll(){var y=window.scrollY;if(nav)nav.classList.toggle('scrolled',y>80);
    if(bg)bg.style.transform='translateY('+(y*0.4)+'px) scale(1.06)';if(hh)hh.style.transform='translateY('+(y*0.18)+'px)';}
  window.addEventListener('scroll',onScroll,{passive:true});onScroll();
  var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target);}});},{threshold:0.12,rootMargin:'0px 0px -80px 0px'});
  document.querySelectorAll('.reveal, .reveal-stagger').forEach(function(el){io.observe(el);});
  var cio=new IntersectionObserver(function(es){es.forEach(function(e){if(!e.isIntersecting)return;var el=e.target,to=parseInt(el.dataset.to,10),st=performance.now();
    function tick(n){var t=Math.min(1,(n-st)/1600);el.textContent=Math.round(to*(1-Math.pow(1-t,3)));if(t<1)requestAnimationFrame(tick);}
    requestAnimationFrame(tick);cio.unobserve(el);});},{threshold:0.5});
  document.querySelectorAll('.counter').forEach(function(el){cio.observe(el);});
  var lb=document.getElementById('lightbox'),li=document.getElementById('lightbox-img');
  if(lb){document.querySelectorAll('.gallery .g-item').forEach(function(it){it.addEventListener('click',function(){li.src=it.querySelector('img').src;lb.classList.add('open');});});
    lb.addEventListener('click',function(e){if(e.target!==li)lb.classList.remove('open');});
    document.addEventListener('keydown',function(e){if(e.key==='Escape')lb.classList.remove('open');});}
  var f=document.getElementById('bookingForm');
  if(f){f.addEventListener('submit',async function(e){e.preventDefault();
    var btn=document.getElementById('f-btn'),st=document.getElementById('f-status'),d=f.dataset,label=btn.innerHTML;
    btn.disabled=true;btn.textContent=d.sending;
    function v(id){var x=document.getElementById(id);return x?x.value:'';}
    var data={secret:'asferia2026secret',name:v('f-name'),phone:v('f-phone'),email:v('f-email'),tour:v('f-tour')+' ('+d.tag+')',date:v('f-date'),people:v('f-people')};
    try{var r=await fetch('https://asferia-bot-production.up.railway.app/booking',{method:'POST',headers:{'Content-Type':'application/json','X-Secret':'asferia2026secret'},body:JSON.stringify(data)});
      if(!r.ok)throw new Error();btn.textContent='✓ '+d.sent;btn.style.background='#3B4A3F';st.textContent=d.sentmsg;st.style.color='';st.style.display='block';f.reset();
    }catch(err){btn.disabled=false;btn.innerHTML=label;st.textContent=d.err;st.style.color='#e07070';st.style.display='block';}
  });}
})();
