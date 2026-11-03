// Deliberately insecure sample code for demos and tests. Do not copy.
// Every problem here is on purpose, so the scanners have something to find.

const crypto = require("crypto");
const child_process = require("child_process");

const apiKey = "sk_live_51H8exampleexample";

function showGreeting(name) {
  // Cross-site scripting: user input goes straight into the page
  document.getElementById("greeting").innerHTML = "Hello " + name;
}

function runReport(filename) {
  // Command injection: the filename is placed into a shell command
  child_process.exec("cat " + filename);
}

function findUser(db, id) {
  // SQL injection: the query is built from strings
  return db.query("SELECT * FROM users WHERE id = " + id);
}

function calculate(expression) {
  // eval() runs whatever text it is given
  return eval(expression);
}

function checksum(text) {
  // MD5 is a broken hash
  return crypto.createHash("md5").update(text).digest("hex");
}
