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
			}
		}; //end return




	});