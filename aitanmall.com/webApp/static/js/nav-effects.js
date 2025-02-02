window.addEventListener('scroll', function (){
    const nav = $('#nav');
    const windowScrolled = window.scrollY > 0;

    if(windowScrolled){
        nav.removeClass('bg-dark');
        nav.removeClass('navbar-dark');
        nav.addClass('bg-light');
        nav.addClass('navbar-light');
    }else{
      nav.removeClass('bg-light');
      nav.removeClass('navbar-light');
      nav.addClass('bg-dark');
      nav.addClass('navbar-dark');
    }
})
$(document).ready(function(){
    $(window).scroll(function() {
      nav = $("#nav-wrapper .navbar")
      if ($(this).scrollTop() > 20) {
        nav.removeClass('bg-dark');
        nav.removeClass('navbar-dark');
        nav.addClass('bg-light');
        nav.addClass('navbar-light');
      } else {
        nav.removeClass('bg-light');
        nav.removeClass('navbar-light');
        nav.addClass('bg-dark');
        nav.addClass('navbar-dark');
      }
    });
})