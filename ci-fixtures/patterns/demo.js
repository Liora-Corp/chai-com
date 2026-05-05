'use strict'

function buildLookupQuery (email) {
  return "SELECT * FROM Users WHERE email = '" + email + "'"
}

function runDynamicExpression (expression) {
  return eval(expression)
}

module.exports = {
  buildLookupQuery,
  runDynamicExpression
}
