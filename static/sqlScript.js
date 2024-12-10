var editor;
document.addEventListener('DOMContentLoaded', function () {
    editor = CodeMirror.fromTextArea(document.getElementById('editor'),{
    mode:'sql',
    theme:'monokai',
    lineNumbers:true,
    autoCloseBrackets:true,
    autoCloseTags: true
}) 
});
function clearer(){
    editor.setValue('');
} 

function downloadSQL() {
        // Get the SQL code from the text area
        var sqlCode = editor.getValue();
        // Create a Blob containing the SQL code
        var blob = new Blob([sqlCode], { type: 'text/plain' });
        // Create a link element
        var a = document.createElement('a');
        // Set the download attribute and file name
        a.download = 'query.sql';
        // Create a URL for the Blob and set it as the href attribute
        a.href = window.URL.createObjectURL(blob);
        // Append the link to the body
        document.body.appendChild(a);
        // Click the link to trigger the download
        a.click();
        // Remove the link element from the DOM
        document.body.removeChild(a);
    }
    function loadSQL() {
        debugger;
        console.log("Entered!!");
        var fileInput = document.createElement('input');
        fileInput.type = 'file';
        // Set accept attribute to restrict file types to HTML
        fileInput.accept = '.sql';
        console.log("Entered!!" + fileInput);
        fileInput.click();
       // Listen for changes in the file input
        fileInput.addEventListener('change', function() {
            var selectedFile = fileInput.files[0];
            if (selectedFile) {
                var reader = new FileReader();
                reader.onload = function(e) {
                    var texter = e.target.result;
                    console.log("texter: " + texter);
                    //editor.setValue(texter.toString())
                    editor.setValue(texter.toString());
                    // console.log("Value is: "+editor.setValue());
                };
                reader.onerror = function() {
                    alert(reader.error);
                  }; 
                reader.readAsText(selectedFile);
            } else {
                alert('Please select a .sql file to load.');
            }
    })
        ;
    }