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

const deleteRoomGroupElements = Array.from(document.getElementsByClassName('form_delete_room_group'));
addEventListenerForDeleteRowButtons(deleteRoomGroupElements, dialogSuccess, dialogError, 
    'Delete Room Group', 'Are you sure you want to delete this room group? Any related rooms and events will also be deleted.')
