const url = 'http://10.1.35.1:8080/api/v1/vehicle/'

export const fetchVehicle = async () => {
    return fetch(url, {})
    .then(res => res.json())
    .then(data => {
        return data
    });
}