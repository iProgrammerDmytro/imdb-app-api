from rest_framework import serializers

from django.db.models import Count

from core.models import Movie, Actor


class ActorSerializer(serializers.ModelSerializer):
    """Serializer for the actor objects"""

    number_of_movies = serializers.SerializerMethodField(
        'get_number_of_movies'
    )
    top_genre = serializers.SerializerMethodField(
        'get_top_genre'
    )
    number_of_movies_by_genre = serializers.SerializerMethodField(
        'get_number_of_movies_by_genre'
    )

    most_frequent_partner = serializers.SerializerMethodField(
        'get_most_frequent_partner'
    )

    def get_most_frequent_partner(self, actor):
        # movie_id_list = []
        number_of_shared_movies = {}

        """Get the current actor"""
        actor = Actor.objects.get(id=actor.id)
        """Get all actor movies"""
        movie_id_list = [role.movie.id for role in actor.role_set.all()]

        """Get number of shared movies with actor id"""
        for movie_id in movie_id_list:
            movie = Movie.objects.get(id=movie_id)
            for role in movie.role_set.all():
                if role.actor.id in number_of_shared_movies:
                    number_of_shared_movies[role.actor.id] += 1
                else:
                    number_of_shared_movies.update({role.actor.id: 1})

        """Delete most common actor because it's current actor object"""
        del number_of_shared_movies[max(
            number_of_shared_movies, key=number_of_shared_movies.get)]

        """Get most frequent partner Actor object"""
        most_frequent_partner = Actor.objects.get(
            id=max(number_of_shared_movies, key=number_of_shared_movies.get))

        result = {
            'partner_actor_id': most_frequent_partner.id,
            'partner_actor_name': f'{most_frequent_partner.first_name} {most_frequent_partner.last_name}',
            'number_of_shared_movies': number_of_shared_movies[most_frequent_partner.id]
        }

        return result

    def get_number_of_movies_by_genre(self, actor):
        """Get number of movies by genre"""
        genre_count = {}
        actor = Actor.objects.get(id=actor.id)

        for role in actor.role_set.all():
            for genre in role.movie.moviegenre_set.all():
                if genre.genre in genre_count:
                    genre_count[genre.genre] += 1
                else:
                    genre_count.update({genre.genre: 1})

        return genre_count

    def get_top_genre(self, actor):
        """Get the top genre for the actor"""
        genre_count = self.get_number_of_movies_by_genre(actor)

        try:
            top_genre = max(genre_count, key=genre_count.get)
        except ValueError:
            top_genre = 'Actor play in a film with no genre'

        return top_genre

    def get_number_of_movies(self, actor):
        """Get the number of movies for the actor"""
        actors = Actor.objects.select_related().annotate(
            number_of_movies=Count('role__movie')
        )

        return actors.get(id=actor.id).number_of_movies

    class Meta:
        model = Actor
        fields = ('id', 'first_name', 'last_name',
                  'top_genre', 'number_of_movies', 'number_of_movies_by_genre', 'most_frequent_partner')