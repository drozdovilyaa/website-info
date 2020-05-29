function load_button() {
    var button = $('#loading_btn');
    var loadingText = '<i class="fa fa-circle-o-notch fa-spin"></i> loading...';
    if (button.html() !== loadingText) {
      button.data('original-text', button.html());
      button.html(loadingText);
    }
  };