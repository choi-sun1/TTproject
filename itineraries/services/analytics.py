class ItineraryAnalytics:
    def generate_report(self, itinerary):
        """여행 통계 생성"""
        return {
            'total_distance': self.calculate_total_distance(),
            'total_expenses': self.calculate_expenses(),
            'time_distribution': self.analyze_time_distribution(),
            'place_categories': self.analyze_place_categories()
        }
