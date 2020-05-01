window.addEventListener('load', function() {
    var x = document.getElementsByTagName('input');
    var i;
    for (i = 0; i < x.length; i++) {
      x[i].setAttribute('autocomplete', 'off');
    }
})


