  $(document).ready(function() {
    $('#id_extracurricular').on('change', function() {
        const firstSelectValue = $(this).val();
        const secondSelect = $('#id_students');

        // Clear current options
        secondSelect.empty();

        // URL for the API request (replace with your actual API endpoint)
        // const apiUrl = `https://pmbp.smasitalbinaa.com/extracurriculars/get-members/?query=${firstSelectValue}`;
        const apiUrl = `https://smait.albinaa.sch.id/pmbp/extracurriculars/get-members/?query=${firstSelectValue}`;

        // Fetch options from the API
        $.getJSON(apiUrl, function(data) {
            // Assuming the API returns an array of options like:
            // [{ "id": 1, "student_class": "10A", "student_name": "John Doe" }, ...]

            $.each(data, function(index, option) {
                secondSelect.append($('<option>', {
                    value: option.id,
                    text: `(${option.student_class__class_name}) ${option.student_name}`
                }));
                secondSelect.css("height",  "6em")

            });
        }).fail(function(jqxhr, textStatus, error) {
            console.error('Error fetching options:', error);
            // Handle errors here
        });

        
      });

    $('#unselectAll').hide()
    $('#selectAll').click(function() {
        $('#id_students option').prop('selected', true);
        $('#unselectAll').show()
        $(this).hide()
    });

    $('#unselectAll').click(function() {
        $('#id_students option').prop('selected', false);
        $('#selectAll').show()
        $(this).hide()
    });

});