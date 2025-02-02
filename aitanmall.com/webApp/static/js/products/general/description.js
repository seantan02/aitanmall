const contentNavigatorBtn = $('.navigator');
const contentNavigator = $('.content');
contentNavigatorBtn.click(function(){
    var navigatorBtnTarget= $(this).data("content");
    resetNavigator();
    showNavigatorContent(navigatorBtnTarget);
})

function showNavigatorContent(target){
    $('#navigator'+target).addClass('active');
    $('#content'+target).addClass('active');
}
function resetNavigator(){
    contentNavigatorBtn.removeClass('active');
    $('.content').removeClass('active');
}