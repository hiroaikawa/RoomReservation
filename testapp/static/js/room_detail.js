const dialogSuccess = document.getElementsByClassName('dialog_success')[0];
const dialogError = document.getElementsByClassName('dialog_error')[0];

dialogSuccess.getElementsByClassName('button_ok')[0].onclick = function () {
  dialogSuccess.close();
  location.reload();
};

dialogError.getElementsByClassName('button_ok')[0].onclick = function () {
  dialogError.close();
  location.reload();
};

const form = document.getElementsByClassName('form')[0];
addEventListenerForForm(form, dialogSuccess, dialogError);
