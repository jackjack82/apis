// example of API requests to https://www.mapbox.com/

const chalk = require('chalk')
const request = require('request')
const yargs = require('yargs')

// without yargs, we can call "process.argv[2]"
//console.log(process.argv)
// address = yargs.argv.address

address = "Torino"

const geocode = (address, callback) => {
    const url = 'https://api.mapbox.com/geocoding/v5/mapbox.places/' + address +
        '.json?access_token=pk.eyJ1IjoiamFja2phY2s4MiIsImEiOiJjazhtd3l1bjkwZzQyM2VxejUxZm40dXVoIn0.1M6X9qT_0avvwR1Lz_jJmA&limit=1'

    request({ url, json: true }, (error, { body }) => {
        if (error) {
            // callback has to return two elements, so we set the second as undefined!
            callback('Unable to connect to location services!', undefined)
        } else if (body.features.length === 0) {
            callback('Unable to find location. Try another search.', undefined)
        } else {
            callback({
                latitude: body.features[0].center[1],
                longitude: body.features[0].center[0],
                location: body.features[0].place_name
            })
        }
    })
}

const printGeocode = (address, callback) => {
    geocode(address, ({latitude, longitude, location}) => {
        callback({latitude, longitude, location})
    })
}

printGeocode(address, ({latitude, longitude, location}) => {
    console.log(latitude, longitude, location)
})

// yargs.command({
//     command: 'address',
//     describe: 'Include the address',
//     builder: {
//         address: {
//             describe: 'Address',
//             demandOption: true,
//             type: 'string',
//         },
//     },
//     handler(argv) {
//         console.log('Starting...')
//         printGeocode(argv.address)
//     }
// })

// if(yargs.parse() === false){
//     console.log(chalk.red.inverse('Missing address arguments!'))
// }


// module.exports = geocode >> return in case of required by other fileds
// console.log(geocode)