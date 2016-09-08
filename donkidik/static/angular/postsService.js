angular.module('DonkidikApp')
	.factory('postsService', function($http){
		$http.defaults.headers.post["Content-Type"] = "application/x-www-form-urlencoded";
		return {
			
			get_types: function(){
				return $http.get('/api/post/types/').then(function(res){
					return res.data;
				});
			},

			get_posts_from_server: function(){
				var url = '/api/posts/all/';
				return $http.get(url).then(function(res){
					// TODO check success here
					return res.data;
				}); // currently dont need additional processing


			}, //end get_posts_from_server

			add_post_comment: function(pid, text){
				var url = '/api/post/' + pid +'/add_comment/';
				return $http({
								method: 'POST',
								url: url,
								data: {text: text}
								}).then(function(res){
					return res.data;
				});
			},

			remove_post: function(pid){
				var url = '/api/post/remove/'+pid+'/';
				return $http.post(url).then(function(res){
					return res.data;
				});
			},

			post_upvote: function(pid){
				var url = '/api/post/'+pid+'/upvote/'
				return $http.post(url).then(function(res){
					return res.data;
				});
			},

			post_downvote: function(pid){
				var url = '/api/post/'+pid+'/downvote/'
				return $http.post(url).then(function(res){
					return res.data;
				});
			}
		}; //end return




	});