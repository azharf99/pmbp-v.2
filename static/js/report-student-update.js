  $('#unselectAll').hide()
  $('#selectAll').hide()
  $(document).ready(()=>{
    $('#id_students').selectize({
          sortField: 'text',
          maxItems: 100,
      });
  })