function addEventListenerForForm(form, dialogSuccess, dialogError){
  form.addEventListener('submit', event => {
      event.preventDefault();
      let formData = new FormData( form );
      let ajaxArg = {
        url : event.submitter.formAction,
        dataType: "html",
        type : event.submitter.formMethod,
        data : formData,
        processData: false,
        contentType: false
      }
    
      $.ajax(ajaxArg).done(function(data, textStatus, jqXHR) {
        let resDataDict = JSON.parse(data);
        dialogSuccess.showModal();
      }).fail(function(jqXHR, textStatus, errorThrown) {
        let result_detail = dialogError.getElementsByClassName('dialog_result_detail')[0];
        let data = JSON.parse(jqXHR.responseText);
        result_detail.textContent = data['message'];
        dialogError.showModal();
      });
    
    }, { passive: false });
}
