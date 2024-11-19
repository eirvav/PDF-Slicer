const url = `/uploads/${pdfFilename}`;

let pdfDoc = null,
    numPages = 0;

// Configure PDF.js
pdfjsLib.GlobalWorkerOptions.workerSrc = '/static/pdfjs/pdf.worker.js';

// Load the PDF
pdfjsLib.getDocument(url).promise.then(function(pdf) {
    pdfDoc = pdf;
    numPages = pdf.numPages;

    // Render all pages
    for (let pageNum = 1; pageNum <= numPages; pageNum++) {
        renderPage(pageNum);
    }
});

function renderPage(num) {
    pdfDoc.getPage(num).then(function(page) {
        const viewport = page.getViewport({ scale: 1.5 });
        const canvas = document.createElement('canvas');
        const context = canvas.getContext('2d');

        canvas.height = viewport.height;
        canvas.width = viewport.width;
        canvas.classList.add('pdf-page');
        canvas.setAttribute('data-page-number', num);

        // Add click event to select/deselect pages
        canvas.addEventListener('click', function() {
            this.classList.toggle('selected');
        });

        // Render the page into the canvas
        page.render({
            canvasContext: context,
            viewport: viewport
        }).promise.then(function() {
            document.getElementById('pdf-container').appendChild(canvas);
        });
    });
}

// Handle the process button click
document.getElementById('process-btn').addEventListener('click', function() {
    const selectedPages = document.querySelectorAll('.pdf-page.selected');
    const pagesToKeep = [];

    selectedPages.forEach(function(canvas) {
        pagesToKeep.push(canvas.getAttribute('data-page-number'));
    });

    if (pagesToKeep.length === 0) {
        alert('Please select at least one page.');
        return;
    }

    // Send selected pages to the server
    fetch('/process', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ filename: pdfFilename, pagesToKeep })
    })
    .then(response => response.json())
    .then(data => {
        // Redirect to download URL
        window.location.href = data.url;
    });
});
