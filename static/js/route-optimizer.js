class RouteOptimizer {
    constructor() {
        this.directionsService = new google.maps.DirectionsService();
    }

    async optimizeRoute(places) {
        if (!places || places.length < 2) {
            return places;
        }

        try {
            // 거리 행렬 계산
            const distanceMatrix = await this._calculateDistanceMatrix(places);
            // TSP 알고리즘을 사용하여 최적 경로 계산 (Nearest Neighbor 알고리즘)
            const optimizedIndices = this._findOptimalRoute(distanceMatrix);
            
            // 최적화된 경로 순서대로 장소 재배열
            return optimizedIndices.map(index => places[index]);
        } catch (error) {
            console.error('경로 최적화 실패:', error);
            return places;
        }
    }

    async _calculateDistanceMatrix(places) {
        const matrix = [];
        for (let i = 0; i < places.length; i++) {
            const row = [];
            for (let j = 0; j < places.length; j++) {
                if (i === j) {
                    row.push(0);
                    continue;
                }
                try {
                    const distance = await this._getDistance(places[i], places[j]);
                    row.push(distance);
                } catch (error) {
                    row.push(Infinity);
                }
            }
            matrix.push(row);
        }
        return matrix;
    }

    async _getDistance(origin, destination) {
        return new Promise((resolve, reject) => {
            this.directionsService.route({
                origin: { lat: origin.latitude, lng: origin.longitude },
                destination: { lat: destination.latitude, lng: destination.longitude },
                travelMode: google.maps.TravelMode.DRIVING
            }, (result, status) => {
                if (status === google.maps.DirectionsStatus.OK) {
                    resolve(result.routes[0].legs[0].distance.value);
                } else {
                    reject(new Error(`경로 계산 실패: ${status}`));
                }
            });
        });
    }

    _findOptimalRoute(distanceMatrix) {
        const n = distanceMatrix.length;
        const visited = new Array(n).fill(false);
        const route = [];

        // 시작점은 첫 번째 장소
        let currentIndex = 0;
        route.push(currentIndex);
        visited[currentIndex] = true;

        // 나머지 장소들에 대해 가장 가까운 곳을 선택
        while (route.length < n) {
            let nextIndex = -1;
            let minDistance = Infinity;

            for (let j = 0; j < n; j++) {
                if (!visited[j] && distanceMatrix[currentIndex][j] < minDistance) {
                    minDistance = distanceMatrix[currentIndex][j];
                    nextIndex = j;
                }
            }

            if (nextIndex === -1) break; // 더 이상 방문할 장소가 없음

            route.push(nextIndex);
            visited[nextIndex] = true;
            currentIndex = nextIndex;
        }

        return route;
    }

    // 시간대별 교통량을 고려한 최적화
    async optimizeWithTraffic(places, departureTime) {
        const matrix = await this._calculateTimeBasedMatrix(places, departureTime);
        const optimizedIndices = this._findOptimalRoute(matrix);
        return optimizedIndices.map(index => places[index]);
    }

    async _calculateTimeBasedMatrix(places, departureTime) {
        const matrix = [];
        for (let i = 0; i < places.length; i++) {
            const row = [];
            for (let j = 0; j < places.length; j++) {
                if (i === j) {
                    row.push(0);
                    continue;
                }
                try {
                    const duration = await this._getTravelTime(
                        places[i],
                        places[j],
                        departureTime
                    );
                    row.push(duration);
                } catch (error) {
                    row.push(Infinity);
                }
            }
            matrix.push(row);
        }
        return matrix;
    }

    async _getTravelTime(origin, destination, departureTime) {
        return new Promise((resolve, reject) => {
            this.directionsService.route({
                origin: { lat: origin.latitude, lng: origin.longitude },
                destination: { lat: destination.latitude, lng: destination.longitude },
                travelMode: google.maps.TravelMode.DRIVING,
                drivingOptions: {
                    departureTime: departureTime,
                    trafficModel: 'bestguess'
                }
            }, (result, status) => {
                if (status === google.maps.DirectionsStatus.OK) {
                    resolve(result.routes[0].legs[0].duration_in_traffic.value);
                } else {
                    reject(new Error(`교통 정보 계산 실패: ${status}`));
                }
            });
        });
    }
}

const optimizer = new RouteOptimizer();
const optimizedRoute = await optimizer.optimizeRoute(places);
// or
const trafficOptimizedRoute = await optimizer.optimizeWithTraffic(places, new Date());