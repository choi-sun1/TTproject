from datetime import datetime
import googlemaps

class TransportService:
    def __init__(self, api_key):
        self.gmaps = googlemaps.Client(key=api_key)

    def get_route(self, origin, destination, mode='transit'):
        now = datetime.now()
        directions = self.gmaps.directions(
            origin,
            destination,
            mode=mode,
            departure_time=now
        )
        return self._process_route_data(directions)

    def _process_route_data(self, directions):
        if not directions:
            return None
        
        route = directions[0]
        return {
            'distance': route['legs'][0]['distance']['text'],
            'duration': route['legs'][0]['duration']['text'],
            'steps': self._extract_steps(route['legs'][0]['steps'])
        }

    def _extract_steps(self, steps):
        return [{'instruction': step['html_instructions'],
                'distance': step['distance']['text'],
                'duration': step['duration']['text']}
                for step in steps]
