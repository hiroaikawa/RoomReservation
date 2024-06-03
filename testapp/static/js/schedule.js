dayjs.extend(dayjsPluginUTC.default)

function toUtcStr(localStr) {
  let dateObj = new Date(localStr);
  let utcStr = dayjs.utc(dateObj).format('YYYY-MM-DD HH:mm:ss');
  return {
    date: dateObj, utcStr: utcStr
  }
}

let resources = [];
roomList.forEach((v, i) => {
  resources.push({ id: Number(v.id), title: v.name });
});

// TODO: Not close modal even if the scroll bar is operated.
const flatpickrOpt = {
  enableTime: true,
  defaultDate: new Date(),
  minuteIncrement: 1,
  allowInput: true,
  static: true,
};

let fpStart = flatpickr('.dialog_edit_mtg .start_time_shown', flatpickrOpt);
let fpEnd = flatpickr('.dialog_edit_mtg .end_time_shown', flatpickrOpt);

const dialogForEdit = document.getElementsByClassName('dialog_edit_mtg')[0];
const dialogSuccess = document.getElementsByClassName('dialog_success')[0];
const dialogError = document.getElementsByClassName('dialog_error')[0];
const formForEdit = dialogForEdit.getElementsByClassName('form')[0];

let previousDayViewType = '';

let events = [];
meetingList.forEach((v, i) => {
  events.push({
    id: Number(v.meeting_id),
    resourceIds: [Number(v.room_id)],
    start: new Date(v.start_time),
    end: new Date(v.end_time),
    title: v.meeting_name,
    startEditable: false,
    durationEditable: false,
  });
});

ec = undefined;
ec = new EventCalendar(document.getElementById('ec'), {
  resources,
  events,
  view: initialView != null ? initialView : 'dayGridMonth',
  allDaySlot: false,
  nowIndicator: true,
  selectable: getSelectable('dayGridMonth'),
  unselectCancel: ['.dialog_edit_mtg', '.dialog_success', '.dialog_error'],
  select: selectFunc,
  dateClick: dateClickFunc,
  eventClick: eventClickFunc,
  headerToolbar: {
    start: 'prev,next today', center: 'title', end: 'dayGridMonth resourceTimeGridDay,resourceTimelineDay'
  },
  titleFormat: getTitleFormat('dayGridMonth'),
  eventTimeFormat: function (start, end) {
    return '';
  },
  viewDidMount: viewDidMountFunc,
  longPressDelay: 300,
  dayMaxEvents: true,
  slotLabelFormat: function (time){
    return String(time.getHours());
  },
  date: initialJsonDate != null ? new Date(initialJsonDate) : new Date()
});

function selectFunc(info){
  if (info.view.type === 'dayGridMonth'){
    ec.unselect();
  } else {
    showModalForCreate(info);
  }
}

function dateClickFunc(info){
  if (info.view.type === 'dayGridMonth'){
    ec.setOption('date', info.date);
    let viewType = previousDayViewType === '' ? 'resourceTimeGridDay' : previousDayViewType;
    ec.setOption('view', viewType);
    ec.unselect();
  }
}

function eventClickFunc(info){
  if (info.view.type === 'dayGridMonth'){
    ec.setOption('date', info.event.start);
    let viewType = previousDayViewType === '' ? 'resourceTimeGridDay' : previousDayViewType;
    ec.setOption('view', viewType);
  }
  else
  {
    showModalForEdit(info.event);
  }
}

function viewDidMountFunc(view) {
  if ( ec === undefined ){
    return;    
  }
  if (view.type !== 'dayGridMonth'){
    previousDayViewType = view.type;
  }

  ec.setOption('titleFormat', getTitleFormat(view.type));
  ec.setOption('selectable', getSelectable(view.type));
}

function getTitleFormat(viewType){
  if (viewType === 'dayGridMonth'){
    return titleFormatFuncForMonthView;
  }
  else {
    return titleFormatFuncForDayView;
  }
}

function getSelectable(viewType){
  return (viewType !== 'dayGridMonth');
}

function titleFormatFuncForMonthView (start, end) {
  const s = new Intl.DateTimeFormat('en', { month: 'short'}).format(start)
  + ' ' + start.getFullYear();
  return { html: s };
}

function titleFormatFuncForDayView (start, end) {
  const s = dayjs(start).toDate().toDateString();
  return { html: s };
}

function clearValidationErrorStr(){
  let elems = Array.from(formForEdit.getElementsByClassName('validation_error'));
  let elem = elems.find(e => e.attributes['name'].value === "end_time_shown");
  elem.style.display = 'none';
}

function showModalForCreate(info) {
  function getResourceTitle(resourceId) {
    const resource = resources.find(r => r.id == resourceId);
    return resource ? resource.title : '';
  }
  let dialog = dialogForEdit;

  let titleEle =  formForEdit.getElementsByClassName('dialog_title')[0];
  titleEle.textContent = "New Reservation" 

  let deleteEle = formForEdit.getElementsByClassName('delete')[0];
  let saveEle = dialog.getElementsByClassName('save')[0];
  saveEle.value = "Create"

  dialog.getElementsByClassName('meeting_id')[0].value = '';
  dialog.getElementsByClassName('user_public_id')[0].value = currentUserPublicId;
  dialog.getElementsByClassName('user_name')[0].value = currentUserName;
  dialog.getElementsByClassName('user_id')[0].value = currentUserId;
  dialog.getElementsByClassName('comment')[0].value = '';
  dialog.getElementsByClassName('meeting_name')[0].value = '';
  let resourceId = info.resource.id;

  dialog.getElementsByClassName('room_id')[0].value = resourceId;
  dialog.getElementsByClassName('room_name')[0].innerText = getResourceTitle(resourceId);

  fpStart.setDate(info.start);
  fpEnd.setDate(info.end);

  setFormElementsEditAttr(true, true, deleteEle, saveEle);
  
  clearValidationErrorStr();
  dialog.showModal();
}

function showModalForEdit(event) {
  function getResourceTitle(resourceId) {
    const resource = resources.find(r => r.id == resourceId);
    return resource ? resource.title : '';
  }
  let dialog = dialogForEdit;

  let deleteEle = dialog.getElementsByClassName('delete')[0];
  let saveEle = dialog.getElementsByClassName('save')[0];

  const meeting = meetingList.find(meeting => meeting.meeting_id == event.id);

  deleteEle.style.display = 'block';
  saveEle.style.display = 'block';
  saveEle.value = "Modify"

  let titleEle =  formForEdit.getElementsByClassName('dialog_title')[0]; 
  titleEle.textContent = meeting.meeting_name === '' ? 'Untitiled' : meeting.meeting_name;

  dialog.getElementsByClassName('meeting_id')[0].value = event.id;
  dialog.getElementsByClassName('user_public_id')[0].value = meeting.user_public_id;
  dialog.getElementsByClassName('user_name')[0].value = meeting.user_name;
  dialog.getElementsByClassName('user_id')[0].value = meeting.user_id;
  dialog.getElementsByClassName('comment')[0].value = meeting.comment;
  dialog.getElementsByClassName('meeting_name')[0].value = meeting.meeting_name;
  let resourceId = event.resourceIds[0];

  dialog.getElementsByClassName('room_id')[0].value = resourceId;
  dialog.getElementsByClassName('room_name')[0].innerText = getResourceTitle(resourceId);

  fpStart.setDate(event.start);
  fpEnd.setDate(event.end);

  let isMine = (meeting.user_id === currentUserId);
  setFormElementsEditAttr(isMine, false, deleteEle, saveEle);

  clearValidationErrorStr();
  dialog.showModal();
}

function setAttr(ele, attrName, needEnable) {
  if (needEnable){
    ele.setAttribute(attrName, true);
  }
  else{
    ele.removeAttribute(attrName);
  }
}

function setFormElementsEditAttr(isMine, isCreate, deleteEle, saveEle){
  //Since readonly is not reflected in forms that use flatpickr, comment out the following.
  //dialog.getElementsByClassName('meeting_name')[0].setAttribute('readOnly', !isMine);
  //dialog.getElementsByClassName('start_time_shown')[0].setAttribute('readOnly', !isMine);
  //dialog.getElementsByClassName('end_time_shown')[0].setAttribute('readOnly', !isMine);
  //dialog.getElementsByClassName('comment')[0].setAttribute('readOnly', !isMine);

  setAttr(deleteEle, 'disabled', !isMine || isCreate);
  setAttr(saveEle, 'disabled', !isMine);
}

function setTimesFromTimesShown(dialog) {
  let startTimeConverted = toUtcStr(dialog.getElementsByClassName('start_time_shown')[0].value);
  let endTimeConverted = toUtcStr(dialog.getElementsByClassName('end_time_shown')[0].value);
  dialog.getElementsByClassName('start_time')[0].value = startTimeConverted.utcStr;
  dialog.getElementsByClassName('end_time')[0].value = endTimeConverted.utcStr;
  return {
    start_time: startTimeConverted.date,
    end_time: endTimeConverted.date
  }
}

formForEdit.addEventListener('submit', event => {
  event.preventDefault();
  const submitterClass = event.submitter.className;
  let isValid = true;
  if ( submitterClass == "save" ){
    let res = setTimesFromTimesShown(dialogForEdit);
    let elems = Array.from(formForEdit.getElementsByClassName('validation_error'));
    let elem = elems.find(e => e.attributes['name'].value === "end_time_shown");
    if ( res.end_time < res.start_time ){
      isValid = false;
      
      elem.innerHTML = "End Time must be equal to or later than Start Time."
      elem.style.display = 'block';
    }
    else{
      elem.innerHTML = "";
      elem.style.display = 'none';
    }
  }

  if (!isValid){
    return false;
  }

  let formData = new FormData( formForEdit );

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

dialogForEdit.getElementsByClassName('close_modal')[0].onclick = function () {
  dialogForEdit.close();
};

dialogSuccess.getElementsByClassName('button_ok')[0].onclick = function () {
  dialogSuccess.close();
  dialogForEdit.close();

  reloadKeepingView();
};

dialogError.getElementsByClassName('button_ok')[0].onclick = function () {
  dialogError.close();
  dialogForEdit.close();

  reloadKeepingView();
};

function reloadKeepingView()
{
  let params = new URLSearchParams(location.search);
  params.set('view', ec.getOption('view'));
  params.set('date', ec.getOption('date').toJSON());
  window.location.search = params.toString();
}
