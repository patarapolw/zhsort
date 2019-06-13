const { web } = require("./webpack.common");

module.exports = {
    mode: "production",
    devtool: "source-map",
    ...web
};