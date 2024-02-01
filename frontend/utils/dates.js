export function timestampToReadableDate(timestamp) {
    // Create a new Date object using the timestamp (in milliseconds)
    var date = new Date(timestamp * 1000); // JavaScript works with milliseconds, so we multiply by 1000
    
    // Get the components of the date
    var year = date.getFullYear();
    var month = ('0' + (date.getMonth() + 1)).slice(-2); // Months are zero-based, so we add 1 and pad with '0'
    var day = ('0' + date.getDate()).slice(-2); // Get the day and pad with '0'
    var hours = ('0' + date.getHours()).slice(-2); // Get the hours and pad with '0'
    var minutes = ('0' + date.getMinutes()).slice(-2); // Get the minutes and pad with '0'
    var seconds = ('0' + date.getSeconds()).slice(-2); // Get the seconds and pad with '0'

    // Construct the readable date format (you can adjust this format as per your preference)
    var readableDate = year + '-' + month + '-' + day + ' ' + hours + ':' + minutes + ':' + seconds;

    return readableDate;
}