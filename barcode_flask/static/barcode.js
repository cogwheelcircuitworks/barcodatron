//
// Goes with ../templates/barcodeform.html
// Implements barcode submission functionality
// Mostly about doing ajax posts of barcodes to the server
//
$(function() {

  var main_server_url = "/ajax";
  var local_server_url = "/ajax";

  // XXX You will need to supply
  var auth_key   = "fake_query";
  var job_id     = "";
  var part_no    = "";
  var label_data = "";
  var err = true;

  document.getElementById("barcode_input").focus(); // just aim and shoot

  $("#barcode_form").submit(function( event ) {
    event.preventDefault();
  });

  $("#barcode_input").keyup(function(event){
      if(event.keyCode == 13){  // terminating newline
          process_barcode();
          return false;
      }
      return false;
  });

  //
  // Process incoming barcodes
  //
  function process_barcode() {
    var bc = $("#barcode_input").val();

    //
    // process SBJOB: Barcodes..
    //
    if (bc.match(/^SBJOB:/i)) {
      $("#barcode_div1").hide();
      // show the barcode
      $("#barcode_div1").barcode(bc,"code128",{barHeight:20,barWidth:1,fontSize:12});
      $("#barcode_div1").fadeIn();
      $("#barcode_input").val(''); // clear input field
      job_id = bc.replace('SBJOB:','');
      var form_data = '&action=' + 'sb_get_job_info' + '&arg1=' + job_id; 
      server_ajax_request(main_server_url, form_data,'');
    }
    //
    // process SBPN: Barcodes...
    //
    else
    if (bc.match(/^SBPN:/i) || 
        bc.match(/^TPN:/i) 
        ) {
      $("#barcode_div2").hide();
      // show the barcode
      $("#barcode_div2").barcode(bc,"code128",{barHeight:20,barWidth:1,fontSize:12});
      $("#barcode_div2").fadeIn();
      $("#barcode_input").val(''); // clear input field

      bc = bc.replace('SBPN:','');
      bc = bc.replace('TPN:','');
      part_no = bc;
      var form_data = '&action=' + 'sb_get_part_info' + '&arg1=' + job_id + '&arg2=' + part_no; 
      server_ajax_request(main_server_url, form_data,'');
    } 
    //
    // prcocess SBX (execution) bar codes
    //
    else if (bc.match(/^SBX:/i)) {
      // execute a command
      $("#barcode_div3").barcode(bc,"code128",{barHeight:20,barWidth:1,fontSize:12});
      $("#barcode_div3").fadeIn();
      $("#barcode_input").val(''); // clear input field

      elems = bc.split(':');
      do_what = elems[1];
      var form_data = '&action=' + 
        'sb_execute' + 
        '&arg1=' + do_what + 
        '&arg2=' + job_id + 
        '&arg3=' + part_no;

      if (do_what.match(/genlabel/)) {
        // to print a label, first  get info from main server
        server_ajax_request(main_server_url, form_data,'label_data no_async'); 

        form_data = '&action=' + 
          'sb_execute_local' + 
          '&arg1=' + do_what  + 
          '&arg2=' + encodeURI(label_data) ; // because it has carriage control \n's

        if (! error )
          // then ask local server to print it.
          server_ajax_request(local_server_url, form_data,'no_async'); 

      }
      else
        //
        // non-local. pass up to main server
        //
        server_ajax_request(main_server_url,form_data);
    }
    //
    // Not an SBX prefix
    //
    else {
      //
      // unknown decodes
      //
      $("#barcode_div3").hide();
      // show the barcode
      $("#barcode_div3").barcode(bc,"code128",{barHeight:20,barWidth:1,fontSize:12});
      $("#barcode_div3").fadeIn();
      $("#barcode_input").val(''); // clear input field

      $("#messages").append('Unknown Barcode <br>');
      $("#messages").fadeIn();

    }

  }

  //
  function server_ajax_request(server_url, form_data,how) {
    // issue a command to the server, get data back.
    if (how.match(/no_async/))
      asynchronicity = false; 
    else
    asynchronicity = true;

    $.ajax(
      {
      async      : asynchronicity,
      type       : "post",
      url        : server_url,
      data       : form_data + '&key=' + auth_key,
      dataType   : 'json', // say 'jsonp' to get cross-domain posting capability
      beforeSend : function () { 
          $("#messages").html(''); 
        },
      success: function (json) {
          $("#messages").html(json.as_html);
          $("#messages").fadeIn();
          if (json.err)
            error = true;
          else
            error = false;

          if (how.match(/label_data/)) 
            label_data = json.label_data; 
          return json;
        },
        error: function () {
          $("#messages").append('something bad happened. Server Didn\'t elaborate<br>');
          $("#messages").fadeIn();
          return json
        }
      });
    return false;
  }
});

