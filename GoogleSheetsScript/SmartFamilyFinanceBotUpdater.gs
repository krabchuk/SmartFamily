function doPost(e) {
  var values = [
    [e.parameter.date,
     e.parameter.where,
     e.parameter.sum,
     e.parameter.data]
  ];
  var sheet = SpreadsheetApp.getActive().getSheetByName(e.parameter.sheet);
  var row = sheet.getLastRow() + 1;
  var range = sheet.getRange(row, 1, 1, 4);
  range.setValues(values);
  range.setBackground(e.parameter.color);
  range.setHorizontalAlignment("center");
  range.setBorder(true, true, true, true, true, true);
  sheet.getRange(row, 1).setFontWeight('bold')
  sheet.getRange(row, 3).setFontWeight('bold')
  return ContentService.createTextOutput('ok');
}
