// post service
(function(){

	var _is_success = function(response){
		return (response.data.status && response.data.status == 'OK');
	};

	angular.module('donkidik')
		.factory('postService', function($http){
			return {
				get_posts: function(uid,pid){
					if (uid) var url = '/api/posts/' + uid +'/';
					else if (pid) var url = '/api/posts/' + pid + '/';
					else var url = '/api/posts/all/';
					return $http.get(url).then(function(res){
						if (_is_success(res)) {
							return {
								success: true,
								posts: res.data.data
							};
						}
						else {
							return { success: false };
						}
					});
				},
				get_spots: function(){
					var url = '/api/spots/all/';
					return $http.get(url).then(function(res){
						if (_is_success(res)) {
							return {
								success: true,
								spots: res.data.data
							};
						}
						else {
							return { success: false };
						}
					});
				},
				reload_post_comments: function(pid) {
					var url = '/api/post/' + pid + '/comments/';
					return $http.get(url).then(function(res){
						if (_is_success(res)) {
							return {
								success:true,
								comments: res.data.comments 
							};
						}
						else {
							return { success: false };
						}
					});
				},
				post_comment: function(pid, text){
					var url = '/api/post/' + pid +'/add_comment/',
						params = { text: text };

					return $http.post(url, params).then(function(res){
						return {
							success: _is_success(res)
						};
					});
				},
				delete_post: function(pid){
					var url = '/api/post/remove/' + pid + '/';
					return $http.post(url).then(function(res){
						return {
							success: _is_success(res)
						};
					});
				},
				create_post: function(data){
					var url = '/api/post/add/';
					return $http.post(url, data).then(function(res){
						return {
							success: _is_success(res),
							post: res.data.post,
							error: res.data.error
						};
					});
				},
				post_upvote: function(pid){
					var url = '/api/post/'+pid+'/upvote/';
					return $http.post(url).then(function(res){
						return res.data;
					});
				},

				post_downvote: function(pid){
					var url = '/api/post/'+pid+'/downvote/';
					return $http.post(url).then(function(res){
						return res.data;
					});
				},

				get_user_meta: function(uid){
					var url = '/api/user/' + uid + '/';
					return $http.post(url).then(function(res){
						return {
									success: _is_success(res),
									user: res.data.user
								};
					});
				}
			};
		});

})();