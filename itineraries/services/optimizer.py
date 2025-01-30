try:
    import numpy as np
except ImportError:
    raise ImportError("최적화 기능을 사용하려면 numpy를 설치해야 합니다. pip install numpy를 실행하세요.")

from typing import List, Dict
from ..models import Place

class RouteOptimizer:
    def optimize_route(self, places: List[Dict]) -> List[Dict]:
        try:
            print(f"입력 장소들: {places}")  # 디버깅용
            
            if len(places) < 2:
                return places

            # 좌표 행렬 생성
            coords = np.array([
                [float(place['latitude']), float(place['longitude'])]
                for place in places
            ])
            n = len(coords)
            
            # 거리 행렬 계산
            dist_matrix = np.zeros((n, n))
            for i in range(n):
                for j in range(n):
                    dist_matrix[i][j] = self._haversine_distance(
                        coords[i][0], coords[i][1],
                        coords[j][0], coords[j][1]
                    )

            # Nearest Neighbor 알고리즘으로 최적 경로 찾기
            route = self._nearest_neighbor(dist_matrix)
            
            # 최적화된 순서로 장소 재배열
            optimized_places = [places[i] for i in route]
            
            # 디버깅 정보 출력
            print(f"최적화된 경로: {route}")
            print(f"최적화된 장소들: {optimized_places}")
            
            return optimized_places
            
        except Exception as e:
            print(f"최적화 중 오류 발생: {str(e)}")  # 디버깅용
            raise

    def _haversine_distance(self, lat1, lon1, lat2, lon2):
        """
        두 지점 간의 거리를 계산 (km)
        """
        R = 6371  # 지구의 반경(km)
        
        lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
        c = 2 * np.arcsin(np.sqrt(a))
        return R * c

    def _nearest_neighbor(self, dist_matrix):
        """
        Nearest Neighbor 알고리즘 구현
        """
        n = len(dist_matrix)
        unvisited = set(range(1, n))
        route = [0]
        
        while unvisited:
            last = route[-1]
            next_point = min(unvisited, key=lambda x: dist_matrix[last][x])
            route.append(next_point)
            unvisited.remove(next_point)
            
        return route
