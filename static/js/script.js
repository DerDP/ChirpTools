

var divContainerAppName = document.getElementById("app_name");
var currentApp = document.getElementById("current_app_name").innerHTML;

function select_deselect() {
   var ele = document.getElementsByName('device');
   var checkAll = document.getElementById('checkAll');
   for (var i = 0; i < ele.length; i++) {
      if (ele[i].type == 'checkbox')
         if(checkAll.checked){
            ele[i].checked = true;
         }
         else{
            ele[i].checked = false;
         }
   }
}




// script.js
const popupOverlay_move = document.querySelector("#popup-overlay-move");
const popupOverlay_delete = document.querySelector("#popup-overlay-delete");
const popupOverlay_snipeImport = document.querySelector("#popup-overlay-snipeImport");
const popupContainer = document.querySelector(".popup-container");
const popupContainer_delete = document.querySelector(".popup-container-delete");
const popupContainer_snipeImport = document.querySelector(".popup-container-snipeImport");
const closePopupButton_move = document.getElementById("close-popup-move");
const closePopupButton_delete = document.getElementById("close-popup-delete");
const closePopupButton_snipeImport = document.getElementById("close-popup-snipeImport");
const snipeInfo = document.querySelector(".snipe-info");


function loading() {
   spinner.style.visibility = 'visible';
   body.style.overflow = 'hidden';
}

$( document ).ready(function() {
   body.style.overflow = 'auto';
   spinner.style.visibility = 'hidden';
   $(".snipe-info").each(function(){
      if ($(this).text() == 'True') {
         this.style.color = 'Green';
      }
      else {
         this.style.color = 'Red';
      }
    });


});

window.onpageshow = function(event) {
   if (event.persisted) {
         body.style.overflow = 'auto';
   spinner.style.visibility = 'hidden';
   }
}

function openPopup_move() {
   popupOverlay_move.style.display = "flex";
   setTimeout(() => {
      popupContainer.style.opacity = "1";
      popupContainer.style.transform = "scale(1)";
   }, 100);
}


function openPopup_delete() {
   popupOverlay_delete.style.display = "flex";
   popupContainer_delete.style.opacity = "1";
   popupContainer_delete.style.transform = "scale(1)";

}

function openPopup_snipeImport() {
   popupOverlay_snipeImport.style.display = "flex";
   popupContainer_snipeImport.style.opacity = "1";
   popupContainer_snipeImport.style.transform = "scale(1)";

}


function closePopup_move() {
   popupContainer.style.opacity = "0";
   popupContainer.style.transform = "scale(0.8)";
   setTimeout(() => {
      popupOverlay_move.style.display = "none";
   }, 300);
}

function closePopup_delete() {
   popupContainer.style.opacity = "0";
   popupContainer.style.transform = "scale(0.8)";
   setTimeout(() => {
      popupOverlay_delete.style.display = "none";
   }, 300);
}

function closePopup_snipeImport() {
   popupContainer.style.opacity = "0";
   popupContainer.style.transform = "scale(0.8)";
   setTimeout(() => {
      popupOverlay_snipeImport.style.display = "none";
   }, 300);
}



closePopupButton_move.addEventListener("click", closePopup_move);
closePopupButton_delete.addEventListener("click", closePopup_delete);
closePopupButton_snipeImport.addEventListener("click", closePopup_snipeImport);

function appChange() {
   var x = $("#appDropDown option:selected").text();
   var selected = $("#appDropDown option:selected").text();


   if (selected != currentApp) {

      divContainerAppName.innerHTML = currentApp + " <div class='triangle-right'></div> " + x;
      document.getElementById('submit').style.visibility = 'visible';
      if (selected == "default") {
         divContainerAppName.innerHTML = 'Please select target app';
         document.getElementById('submit').style.visibility = 'hidden';
      }
   } else {
      divContainerAppName.innerHTML = 'Choose another app target to move to!';
      document.getElementById('submit').style.visibility = 'hidden';
   }
}

// On check box change, check if checked or not and enable/disable change buttons

$(".checkbox").change(function() {
   var checkboxes = document.querySelectorAll('input[type=checkbox]:checked');
   var controls = document.getElementsByClassName('controls')[0];
   if(checkboxes.length > 0) {
      controls.style.visibility = 'visible';
   }
   else {
      controls.style.visibility = 'hidden';
   }
});