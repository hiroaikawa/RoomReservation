function addEventListenerForDeleteRowButtons(elements, dialogSuccess, dialogError, confirmModalTitle, confirmModalContent){
  elements.forEach(form => {
      form.addEventListener('submit', event => {
          event.preventDefault();
  
          $("#confirmModalTitle").text(confirmModalTitle);
          $("#confirmModalContent").text(confirmModalContent);
      
          $("#confirmModalYes").on("click", function(e){
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
          });
      
          let modal = new bootstrap.Modal($("#confirmModal"));
          modal.show();
        }, { passive: false });
  })
}