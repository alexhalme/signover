export function range (number) {
  return [...Array(number).keys()]
}

export function zip (arrays) {
  return range(arrays[0].length).reduce((acc, sub) => [acc, [arrays.map(x => x[sub])]].flat(), [])
}

export function dictzip (zipped) {
  return zipped.reduce((acc, obj) => { var temp = {}; temp[obj[0]] = obj[1]; return { ...acc, ...temp } }, {})
}

export function dictlists (arrays) {
  return zip(arrays).reduce((acc, obj) => { var temp = {}; temp[obj[0]] = obj[1]; return { ...acc, ...temp } }, {})
}
