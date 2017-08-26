const fs = require('fs');

const retry = 5;

function run(file, object) {
    return new Promise((resolve, reject) => {
        if (typeof file !== 'string') {
            return reject(new TypeError('File must be a string'));
        }

        if (typeof object !== 'object') {
            return reject(new TypeError('Object must be an object'));
        }

        for (let i = 0; i < retry; i++) {

            fs.writeFile(file, JSON.stringify(object, '', '\t'), 'utf8', (err) => {

                if (err) {
                    if (i >= retry) {
                        reject(err);
                    }
                }

                try {

                    require(file);
                    delete require.cache[require.resolve(file)];
                    resolve();

                } catch(error) {

                    delete require.cache[require.resolve(file)];
                    if (i < retry) {
                        reject(err);
                    }

                }

            });

        }

    });
}

module.exports = run;