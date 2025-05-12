function downloadBlobData(data, filename) {
    const url = window.URL.createObjectURL(
        new Blob([data], { type: "application/vnd.ms-excel" })
    );
    var a = document.createElement("a");
    a.href = url;
    a.setAttribute("download", filename);
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
}

function toCapitalize(string) {
    let words = string.split(' ')
    return words.map((word) => {
        word = word.split('');
        let char = ''
        if (word.length !== 0) {
            char = word[0].toUpperCase();
        }
        word[0] = char
        return word.join('')
    }).join(' ');
}

function toTitleCase(text) {
    text = text.replace("_", " ").replace("-", " ")
    return toCapitalize(text)
}

export { downloadBlobData, toCapitalize, toTitleCase }